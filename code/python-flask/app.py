from flask import Flask, request, redirect, url_for, session, render_template, session
from flask_socketio import SocketIO, emit # Used to connect the lab SSH back to the Python Flask App
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
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

# Instantiate the .env file loader to read the RO Vault TOken
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
socketio = SocketIO(app)
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
                # user = User()
                # user.id = user_info["email"]
                # Store email in Session Variable so other functions can access it
                session['email'] = user_info["email"] #Isn't this redundant with user.id?
                session['uid'] = user_info["sub"]
                # login_user(user)
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
def handle_input(data):
    ssh.send(data)  # Send user input to SSH session

def ssh_thread(ip):
    global ssh
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='vagrant', key_filename='id_ed25519_flask_app_fe_to_launched_edge_server_for_a_lab')
    channel = ssh.invoke_shell()
    while True:
        output = channel.recv(1024).decode()
        socketio.emit('output', output)

##############################################################################
# Function to call the run cmd Flask Route on the API server
def run_cmd(runtime_uuid, lab_num):
    
    url = FLASK_API_SERVER + "/run"
    payload = {'runtime_uuid': runtime_uuid.hex, 'email': session['email'],'lab_number': lab_num } # took out {} from session email
    # Using internal self-signed generated Certs so need to disable verify
    response = requests.post(url, json=payload,verify=False)
    my_dict = dict(status_code=response.status_code, response_text=response.text)


##############################################################################
# Above code deals with login and authentication]
# Below code is lab launching logic
##############################################################################
@app.route("/progress/<task_id>")
def progress_page(task_id):
    return render_template("progress.html", task_id=task_id)
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
@app.route('/lab_one')
@login_required
def lab_one():
    lab_number="lab_one"
    # Generate a UUID to identify this running of the lab
    runtime_uuid = uuid.uuid4()
    # Call SQL Alchemy Helper Function to create a lab record
    new_lab=create_lab_entry(session['email'],lab_number) # took curly brackets out, doesn't like that a set was being used as a key
    
    # Call to the API functions broken down into multiple small functions for better debugging
    task_id = run_cmd(runtime_uuid, lab_number)
    # Render progress page
    progress_page(task_id.id)
    
    
    # Next step is to send a HTTP post request to retrieve the IP address of the edge node
    # for the lab being launched

    get_ip_url = FLASK_API_SERVER + "/getip"
    payload = {'runtime_uuid': runtime_uuid.hex, 'email': session['email'],'lab_number': lab_number } # took out {} from session email
    # Using internal self-signed generated Certs so need to disable verify
    response = requests.post(get_ip_url, json=payload,verify=False)
    ip = response.text # IP address of edge server

    # Establish the SSH connection with the edge node using sockets
    threading.Thread(target=ssh_thread, args=(ip)).start()

    # Open the questions TOML document and read them in as a Python dict to be
    # passed into the shelly.html template and rendered
    # Need to use python3-toml library in Ubuntu 22.04 as Python 3.10 is the default
    # As of Python 3.11 toml is build in to std lib and requires rb
    with open("lab_one.toml", "r") as f:
      lab_questions = toml.load(f)
 
    # This is what the TOML dict looks
    # {
    # "questions": {
    #    "step_one": "Open the terminal on your Linux system.",
    #    "step_two": "Check what user you are logged into. Is it root?"
    #    }
    # }
    # lab_questions["questions"]  the value questions comes from the TOML document top level Dict
    return render_template('shelly.html', qa=lab_questions["questions"], email={session['email']}, response_dict=my_dict )
    # Redirect to shelly
    #return redirect(url_for('.shelly'))
    # return redirect(url_for('.waiting'))  


@app.route('/lab_two')
@login_required
def lab_two():
    # Run lab 2 script
    lab_control()
    # Redirect to shelly
    return redirect(url_for('.shelly'))
    # return redirect(url_for('.waiting'))


@app.route('/lab_three')
@login_required
def lab_three():
    # Run lab 2 script
    lab_control()
    # Redirect to shelly
    return redirect(url_for('.shelly'))
    # return redirect(url_for('.waiting'))

@app.route('/shelly')
@login_required
def shelly():
    return render_template('shelly.html')


@app.route('/end-lab')
@login_required
def endlab():
    # os.system(f"echo '{UUID}, {username}' > /home/vagrant/end-lab-reached")
    with open('/home/vagrant/kali-ip', 'r') as file:
        content = file.read()
        kaliIP = content.strip()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, username=SSH_USER, key_filename=SSH_KEY, port=SSH_PORT)
    command = "source /home/izziwa/.ssh/environment; source /home/izziwa/user-vars; printenv > /home/izziwa/ssh-destroy-env; bash /home/izziwa/lab_destroy.sh"
    stdin, stdout, stderr = client.exec_command(command)
    client.close()
    os.system(f"sed -i 's/{kaliIP}/<IP-HERE>/g' /home/vagrant/oauth-site/templates/shelly.html")
    return redirect(url_for('.launch'))

def lab_control(UUID, username):
    # render_template('waiting.html')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, username=SSH_USER, key_filename=SSH_KEY, port=SSH_PORT)   

    # Pass UUID and username variables to the bash script
    command = "source /home/izziwa/.ssh/environment; bash /home/izziwa/lab_launch.sh " + UUID + " " + username
    stdin, stdout, stderr = client.exec_command(command)
    # Wait for terraform apply to finish
    exitStatus = stdout.channel.recv_exit_status()
    if exitStatus == 0:
        # Retrieve Kali IP
        config = configparser.ConfigParser()
        config.read("config.ini")
        proxmox = ProxmoxAPI(config['DEFAULT']['url'], user=config['DEFAULT']['user'], password=config['DEFAULT']['pass'], verify_ssl=False)

  
    else:
        os.system(f"echo 'Error. Exit code {exitStatus} returned.' > /home/vagrant/get-kali-ip-log")


    client.close()
    # Redirect to shelly
    return redirect(url_for('.shelly'))
