from flask import Flask, request, redirect, url_for, session, render_template, session
from flask_socketio import SocketIO, emit # Used to connect the lab SSH back to the Python Flask App
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from proxmoxer import ProxmoxAPI
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
import hvac
import uuid
import logging
from systemd.journal import JournalHandler
from dotenv import load_dotenv
import os, paramiko, threading, re, time, requests
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.dialects.mysql import CHAR # adding imports that specifically bring in the defined char
from sqlalchemy.dialects.postgresql import UUID # adding uuid()
from sqlalchemy import Column, String, func # different syntax to explicitly call for the uuid() func
import toml # Import TOML library from Python standard lib 3.11 or <
# https://copilot.microsoft.com/shares/vQLqNAfQEewvPxt7fUXph

# Initialize logging object to send logs to the journal
logger = logging.getLogger('cyberrange')
journald_handler = JournalHandler()
journald_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger.addHandler(journald_handler)
logger.setLevel(logging.INFO)

# Instantiate the .env file loader to read the RO Vault Token
load_dotenv()

# Initialize Vault client
# Added Verify=False, remove hardcoded token for production use
client = hvac.Client(url='https://jrh-vault-instance-vm0.service.consul:8200', token=os.getenv('TOKEN'), verify=False)

##############################################################################
# Read run time access secrets from the CR vault key-pair
##############################################################################
creds = client.read('secret/data/CR')

# Extract username and password
client_id = creds['data']['data']['CLIENT_ID']
client_secret = creds['data']['data']['CLIENT_SECRET']
APP_SECRET = creds['data']['data']['APP_SECRET']
# Retrieve Proxmox Token connection to execute terraform apply
# Added by JRH
CR_TOKEN_ID = creds['data']['data']['CR_TOKEN_ID']
CR_TOKEN_VALUE = creds['data']['data']['CR_TOKEN_VALUE']
CR_PROXMOX_URL = creds['data']['data']['CR_PROXMOX_URL']
FLASK_API_SERVER = creds['data']['data']['FLASK_API_SERVER']
DBUSER = creds['data']['data']['DBUSER']
DBPASS = creds['data']['data']['DBPASS']
DBURL = creds['data']['data']['DBURL']
DATABASENAME = creds['data']['data']['DATABASENAME']

##############################################################################
# Instantiate application
##############################################################################
app = Flask(__name__)
socketio = SocketIO(app) # might move to helper function, called multiple times to instantiate multiple times
##############################################################################
#Initialize SQL Alchemy DB object for SQL
##############################################################################
CONNECTION_STRING = 'mysql+pymysql://' + DBUSER + ':' + DBPASS + '@' + DBURL + '/' + DATABASENAME 
app.config['SQLALCHEMY_DATABASE_URI'] = CONNECTION_STRING
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'Users'  # trying to explicitly set the table name to 'Users' so there is no lowercase
    email = db.Column(db.String, primary_key=True)
    # id = db.Column(db.String(36), unique=True, nullable=False)
    id = Column(CHAR(36), unique=True, server_default=func.uuid()) # new id declaration
    last_login = db.Column(db.DateTime, nullable=False)
    admin_status = db.Column(db.Integer, nullable=False)

class Labs(db.Model):
    __tablename__ = 'Labs'  # trying to explicitly set the table name so there is no lowercase
    # id = db.Column(db.String(36), unique=True, nullable=False)
    id = Column(CHAR(36), server_default=func.uuid()) # new id declaration
    lab_number = db.Column(db.Integer, nullable=False)
    lab_complete = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    last_attempt = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String, primary_key=True)

##############################################################################
# Create Helper functions for DB access
# https://copilot.microsoft.com/shares/MiPTDp2uEjHMXBJyHTJBF
##############################################################################
# This will check if the user already exists in the DB else create
def check_or_create_user(email):
    existing = db.session.execute(select(Users).filter_by(email=email)).scalar_one_or_none()
    if existing:
        return None  # or handle as needed
    new_user = Users(email=email, last_login=datetime.now(timezone.utc))
    db.session.add(new_user)
    db.session.commit()
    return new_user

def select_filtered(model, **filters):
    stmt = select(model).filter_by(**filters)
    return db.session.scalars(stmt).all()

def create_lab_entry(email,lab_number):
    new_lab = Labs(lab_number=lab_number,email=email)
    db.session.add(new_lab)
    db.session.commit()
    return new_lab

##############################################################################
# Flask-Login setup
##############################################################################
app.secret_key = 'APP_SECRET' # Change to point to the vault instance EDIT: Added Manually, add back as 'APP_SECRET'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OAuth configuration
authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
token_url = 'https://accounts.google.com/o/oauth2/token'
redirect_uri = 'https://system60.rice.iit.edu/callback'
scope = ['profile', 'email']

##########################
class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id): #This function does not get called, what is it for?
    user = User()
    user.id = user_id
    return user

@app.route('/')
def index():
    if 'google_token' in session:
        google = OAuth2Session(client_id, token=session['google_token'])
        try:
            response = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
            if 'email' in response:
                #global user_info #Why is this global?
                user_info = response
                user = User()
                user.id = user_info["email"]
                # Store email in Session Variable so other functions can access it
                session['email'] = user_info["email"] #Isn't this redundant with user.id?
                session['uid'] = user_info["sub"]
                ######################################################################################
                '''
                When you call login_user(user):
                
                Stores the user’s ID in the session
                Flask‑Login calls user.get_id() (provided by UserMixin or your own implementation) and 
                saves that ID in Flask’s session cookie.
                This is how Flask‑Login remembers who you are between requests.

                Marks the user as authenticated
                For the rest of the request (and future requests in the same session), current_user 
                will be set to your user object.
                current_user.is_authenticated will return True.

                Triggers login signals
                Sends the user_logged_in signal, which you can hook into for logging, auditing, or
                other side effects.
                Optionally remembers the user
                If you pass remember=True, Flask‑Login will set a long‑lived “remember me” cookie so 
                the user stays logged in even after closing the browser.
                '''                
                login_user(user)
                # Helper function to check if user exists and if not create in DB
                user_in_application = check_or_create_user(user_info['email'])
                # Function to query all of the current lab progress per user account
                lab = select_filtered(Labs, email=user_info['email'])
                # This checks for the UID problem if you reload the index page after a packer/terraform rebuild
                # if user_in_application is None:
                # return redirect(url_for('.index')) 
                # else:
                return render_template('dashboard.html', lab_results=lab, uid = user_info["sub"], email=user_info["email"])
            else:
                return render_template('index.html') #Render template instead?
        except TokenExpiredError:
            if 'refresh_token' in session['google_token']:
                # Refresh expired token
                token = google.refresh_token(
                    token_url,
                    client_id=client_id,
                    client_secret=client_secret,
                    refresh_token=session['google_token'].get('refresh_token')
                )
                session['google_token'] = token
                #return render_template('dashboard.html', lab_results=lab, uid = user_info["sub"], email=user_info["email"])
                return render_template('index.html')
            else:
                # Session expired
                return render_template('index.html')#Where is the login page?
    return render_template('index.html')

@app.route('/login')
def login():
    google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    authorization_url, state = google.authorization_url(authorization_base_url, access_type='offline', prompt='consent')
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    google = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri=redirect_uri)
    token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)
    session['google_token'] = token
    return redirect(url_for('.index'))

@app.route('/logout')
@login_required
def logout():
    session.pop('google_token', None)
    return redirect(url_for('.index'))

@app.route("/test")
@login_required
def hello_world():
    return "<p>Hello, Cyber Range!</p>"

@socketio.on('input')
def handle_input(data): # alter for pyxtermjs
    ssh.send(data)  # Send user input to SSH session

def ssh_thread(ip):
    global ssh # no longer using parimiko so scrap it 
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='vagrant', key_filename='id_ed25519_flask_app_fe_to_launched_edge_server_for_a_lab')
    channel = ssh.invoke_shell()
    while True:
        output = channel.recv(1024).decode()
        socketio.emit('output', output)

##############################################################################
# Function to call the run cmd Flask Route on the API server
def run_cmd(runtime_uuid, lab_num,action):
    
    if action == "run":
        url = FLASK_API_SERVER + "/run"
    else:
        url == FLASK_API_SERVER + "/destroy"

    payload = {'runtime_uuid': runtime_uuid.hex, 'email': session['email'],'lab_number': lab_num } # took out {} from session email
    # Using internal self-signed generated Certs so need to disable verify
    response = requests.post(url, json=payload,verify=False)
    # Parse JSON body
    data = response.json()
    return data['task_id']

##############################################################################
# Above code deals with login and authentication]
# Below code is lab launching logic
##############################################################################
@app.route("/progress/<task_id>")
def progress_page(lab_id, task_id, api_url):
    return render_template("progress.html", lab_id=lab_id, task_id=task_id, api_url=api_url)
##############################################################################
# This route is going to launch the content of the lab.
# This means a few things...
# First step will be communicating via an API the details of the user
# and which lab will be sent over to launch... Launch means on the API side
# which modifications need to be made to the tags so we can ID these VM 
# instances in the lab as well as issue a terraform apply command to have the
# elements of the lab launched...

# Once the elements of the lab have been launched we return control to this 
# function and the user details - gained from the Google Oauth object, along
# with the Questions and Answers are sent into the xterm page.

# This requires that an SSH session be established between the Python Flask
# App and the edge-server of the lab network

# An edge-server is defined as the entry point to the private network 
# defined by a Proxmox Zone that has two interfaces 

# A call to the Flask API will be needed to retrieve this IP and then pass 
# that to the function required to establish the SSH connection and pass that
# to xterm in the shelly.html Flask template...
##############################################################################
@app.route('/launch_lab')
@login_required
def launch_lab():
    lab_number = request.args.get('lab_id')
    # Generate a UUID to identify this running of the lab
    runtime_uuid = uuid.uuid4()
    action = "run"
    # Call SQL Alchemy Helper Function to create a lab record
    new_lab=create_lab_entry(session['email'],lab_number) # took curly brackets out, doesn't like that a set was being used as a key
    
    # Call to the API functions broken down into multiple small functions for better debugging
    # t_id for task id
    t_id = run_cmd(runtime_uuid, lab_number, action)
    # Render progress page
    # progress_page(t_id)
    # return redirect(url_for('.progress_page', task_id=t_id))
    # GOSSIPAPIURL is the internal address that the flask APIserver is listening on
    # This is defined in the .env file and can be found by running: consul catalog nodes
    return render_template("progress.html", lab_id=lab_number, task_id=t_id, api_url=os.getenv('PUBLICAPIURL'), lab_launch_uuid=runtime_uuid, user_email=session['email']) # trying to render progress without task id in URL

##############################################################################
# Destroy lab via issuing the terraform destroy command
##############################################################################
@app.route('/destroy_lab')
@login_required
def destroy_lab():
    lab_number = request.args.get('lab_id')
    launch_id = request.args.get('launch_id')
    # Set this parameter so that the run_cmd celery task runs the /destroy
    # route
    action = "destroy"
    
    # Call to the API functions broken down into multiple small functions for
    # better debugging
    # t_id for task id
    t_id = run_cmd(launch_id, lab_number, action)
    return render_template("dashboard.html") # Go back to the Dashboard

##############################################################################
# Creating function to read lab question .toml files
##############################################################################
def load_lab_steps(lab_id: str):
    filename = f"labs/{lab_id}.toml"
    with open(filename, "r", encoding="utf-8") as f:
        return toml.load(f)

##############################################################################
# Creating function to read lab answer .toml files
##############################################################################
def load_answer_steps(lab_id: str):
    filename = f"labs/{lab_id}_answers.toml"
    with open(filename, "r", encoding="utf-8") as f:
        return toml.load(f)

##############################################################################
# Shelly route will display the page with the xterm js connected via socketio
# to the edge node for this lab
##############################################################################
@app.route('/shelly', methods=['GET', 'POST'])
@login_required
def shelly():
    launch_id = request.args.get('launch_id')
    user_id = request.args.get('user_id')
    lab_id = request.args.get('lab_id')
    ip=run_getip(launch_id)
    # Returns .toml file as a dictionary
    loaded_lab_steps = load_lab_steps(lab_id)
    #steps = loaded_lab_steps.get("questions")
    
    return render_template('shelly.html', lab_id=lab_id, launch_id=launch_id,loaded_lab_steps=loaded_lab_steps, edge_node_ip=ip, user_email=user_id)

##############################################################################
# Helper function to take the returned IP and turn it into an FQDN
##############################################################################
def getFqdn(ip_address):
  import socket

  try:
    fqdn = socket.gethostbyaddr(ip_address)[0]
    return fqdn
  except socket.herror as e:
    return f"Unable to resolve IP: {e}"

##############################################################################
# Route to grade lab submission
##############################################################################
@app.route("/grade_lab", methods=["POST"])
def grade_lab():
    logger.info("The lab_id passed is: %s", request.form.get("lab_id"))
    correct_answers = load_answer_steps(request.form.get("lab_id"))
    answers = correct_answers.get("answers")
    numberOfAnswers = len(correct_answers)
    total = 0
    
    # Grab the a list of the form values
    values_list = list(request.form.values())
    
    for answer in answers:
        for value in values_list:
            if answer == value:
                total += 1

    # Call database function to insert data here
        
    # Do something with the data (e.g., log, process, return response)
    return render_template(
        "shelly.html",
        t=total,
        noa=numberOfAnswers
    )

    #return f"Grand Total of {total} points out of {numberOfAnswers} points..."

##############################################################################
# Helper function to get the IP address of the edge server when user launches
# a lab -- need to take the launch_uuid and search the tags for the VM with
# with that value along with the edge_node tag
##############################################################################
def run_getip(launch_id):
    TOKEN = CR_TOKEN_ID.split('!')
    FQDN = CR_PROXMOX_URL.replace("https://", "")
    proxmox = ProxmoxAPI(FQDN, user=TOKEN[0], token_name=TOKEN[1], token_value=CR_TOKEN_VALUE, verify_ssl=False)

    prxmx42 = proxmox.nodes("system42").qemu.get()
    prxmx41 = proxmox.nodes("system41").qemu.get()

    found42 = False
    found41 = False
    # This replaces the '-' in the launch_id, we removed them when we added them
    # as a tag in Terraform. Terraform doesn't support '-' 
    launch_id=launch_id.replace("-","")

    runningvms = []
    runningwithtagsvms = []
    # Loop through the first node to get all of the nodes that are of status
    # running and that have the tag of the user for vm in prxmx42:
    # and that they have the tag 'edge' meaning they are the edge node
    for vm in prxmx42:
        if vm['status'] == 'running' and str(launch_id) in vm['tags'] and 'edge' in vm['tags']:
            runningvms.append(vm)

            for vm in runningvms:
                runningwithtagsvms.append(proxmox.nodes("system42").qemu(vm['vmid']).agent("network-get-interfaces").get())
                for x in range(len(runningwithtagsvms)):
                    for y in range(len(runningwithtagsvms[x]['result'])):
                        if "192.168.172" in runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address']:
                            found42 = True
                            logging.info("IP found: %s", runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address'])
                            return getFqdn(runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address'])
        
    if found42 == False:
        for vm in prxmx41:
            if vm['status'] == 'running' and str(launch_id) in vm['tags'] and 'edge' in vm['tags']:
                runningvms.append(vm)

                for vm in runningvms:
                    runningwithtagsvms.append(proxmox.nodes("system41").qemu(vm['vmid']).agent("network-get-interfaces").get())
                    for x in range(len(runningwithtagsvms)):
                            for y in range(len(runningwithtagsvms[x]['result'])):
                                if "192.168.172" in runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address']:
                                    logging.info("IP found: %s", runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address'])
                                    return getFqdn(runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address'])

    return None

##############################################################################
