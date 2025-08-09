from flask import Flask, request, redirect, url_for, session, render_template
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
import hvac
from dotenv import load_dotenv
import os, paramiko, threading, re, time
from proxmoxer import ProxmoxAPI
import tomllib # Import TOML library from Python standard lib 3.11 or <
# https://copilot.microsoft.com/shares/vQLqNAfQEewvPxt7fUXph

load_dotenv()
socketio = SocketIO(app)
threading.Thread(target=ssh_thread).start()
socketio.run(app)
####Verified working with Vault#####

# Initialize Vault client
client = hvac.Client(url='https://jrh-vault-instance-vm0.service.consul:8200', token=os.getenv('TOKEN'), verify=False)
# Added Verify=False, remove hardcoded token for production use


# Check authentication
# assert client.is_authenticated()

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
CR_TOKEN_ID = ['data']['data']['CR_TOKEN_ID']
CR_TOKEN_VALUE = ['data']['data']['CR_TOKEN_VALUE']
CR_PROXMOX_URL = ['data']['data']['CR_PROXMOX_URL']

app = Flask(__name__)
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
def load_user(user_id):
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
                global user_info
                # global UUID
                # global username
                user_info = response
                user = User()
                user.id = user_info["email"]
                login_user(user)
                # UUID = str(time.time())
                # UUID = UUID.split('.', 1)[0]
                # username = str(user_info["email"])
                # username = username.split('@', 1)[0]

                #return f'Logged in as {user_info["email"]}<br><a href="/launch">Go to Launch Page</a><br><a href="/logout">Logout</a>'
                return render_template('dashboard.html', email=user_info["email"])
            else:
                return redirect(url_for('.index'))
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
                return redirect(url_for('.index'))
            else:
                # Session expired
                return redirect(url_for('.login'))
    #return 'You are not logged in<br><a href="/login">Login</a>'
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

##############################################################################
# Above code deals with login and authentication]
# Below code is lab launching logic
##############################################################################

##############################################################################
# This route is going to launch the content of the lab.
# This means a few things...
# First step will be communicating via the API with the details of the user
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
    with open("lab-questions.toml", "rb") as f:
      questions = tomllib.load(f)
    # Run lab 1 script
    UUID = str(time.time())
    UUID = UUID.split('.', 1)[0]
    username = str(user_info["email"])
    username = username.split('@', 1)[0]
    username = re.sub('[^A-Za-z0-9]+', '', username)
    lab_control(UUID, username)
    return render_template('shelly.html', qa=questions, email=user_info["email"])
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

        prxmx42 = proxmox.nodes("system42").qemu.get()

        runningvms = []
        runningwithtagsvms = []
        # Loop through the first node to get all of the nodes that are of status running and that have the tag of the user

        for vm in prxmx42:
            if vm['status'] == 'running' and vm['tags'].split(';')[0] == UUID:
                runningvms.append(vm)

        for vm in runningvms:
            runningwithtagsvms.append(proxmox.nodes("system35").qemu(vm['vmid']).agent("network-get-interfaces").get())
            for x in range(len(runningwithtagsvms)):
                for y in range(len(runningwithtagsvms[x]['result'])):
                    if "192.168.100." in runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address']:
                        kaliIP = runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address']
                        # replace with sed command to switch IP in templates/shelly.html
                        os.system(f"sed -i 's/<IP-HERE>/{kaliIP}/g' /home/vagrant/oauth-site/templates/shelly.html")
                        # echo to file so sed can replace the above line later
                        os.system(f"echo '{kaliIP}' > /home/vagrant/kali-ip")
                        break
    else:
        os.system(f"echo 'Error. Exit code {exitStatus} returned.' > /home/vagrant/get-kali-ip-log")


    client.close()
    # Redirect to shelly
    return redirect(url_for('.shelly'))
