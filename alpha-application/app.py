from flask import Flask, request, redirect, url_for, session, render_template
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os, paramiko, threading, re, time
from oauthlib.oauth2 import TokenExpiredError
from proxmoxer import ProxmoxAPI
import configparser

app = Flask(__name__)

load_dotenv()
socketio = SocketIO(app)


#################################################
#                 Paramiko setup                #            
#################################################

SSH_HOST = "192.168.172.114"
SSH_USER = "izziwa"
SSH_PORT = 22
SSH_KEY  = "/home/vagrant/.ssh/izziwa_key"

#################################################
#                                               #
#################################################


# Flask-Login setup
app.secret_key = os.getenv('APP_SECRET') # Change to point to the vault instance
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OAuth configuration
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
token_url = 'https://accounts.google.com/o/oauth2/token'
redirect_uri = 'https://system114.rice.iit.edu:5000/callback'
scope = ['profile', 'email']


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
                ######################################################################################
                '''
                When you call login_user(user):
                
                Stores the user’s ID in the session
                Flask‑Login calls user.get_id() (provided by UserMixin or your own implementation) and saves that ID in Flask’s session cookie.
                This is how Flask‑Login remembers who you are between requests.

                Marks the user as authenticated
                For the rest of the request (and future requests in the same session), current_user will be set to your user object.
                current_user.is_authenticated will return True.

                Triggers login signals
                Sends the user_logged_in signal, which you can hook into for logging, auditing, or other side effects.
                Optionally remembers the user
                If you pass remember=True, Flask‑Login will set a long‑lived “remember me” cookie so the user stays logged in even after closing the browser.
                '''
                login_user(user)
                # UUID = str(time.time())
                # UUID = UUID.split('.', 1)[0]
                # username = str(user_info["email"])
                # username = username.split('@', 1)[0]

                return f'Logged in as {user_info["email"]}<br><a href="/launch">Go to Launch Page</a><br><a href="/logout">Logout</a>'
            else:
                return 'Error: Email not found in user info.<br><a href="/logout">Logout</a>'
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
    return 'You are not logged in<br><a href="/login">Login</a>'


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


@app.route('/launch')
@login_required
def launch():
    # The user is authenticated, show the launch page.
    return render_template('launch-labs.html')


@app.route('/lab1')
@login_required
def lab1():
    # Run lab 1 script
    UUID = str(time.time())
    UUID = UUID.split('.', 1)[0]
    username = str(user_info["email"])
    username = username.split('@', 1)[0]
    username = re.sub('[^A-Za-z0-9]+', '', username)
    lab_control(UUID, username)
    # Redirect to shelly
    return redirect(url_for('.shelly'))
    # return redirect(url_for('.waiting'))  


@app.route('/lab2')
@login_required
def lab2():
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

        prxmx35 = proxmox.nodes("system35").qemu.get()

        runningvms = []
        runningwithtagsvms = []
        # Loop through the first node to get all of the nodes that are of status running and that have the tag of the user

        for vm in prxmx35:
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


'''
@app.route('/waiting')
@login_required
def waiting():
    # renderWaitingPage()
    
    UUID = str(time.time())
    UUID = UUID.split('.', 1)[0]
    username = str(user_info["email"])
    username = username.split('@', 1)[0]
    lab_control(UUID, username)
    return "Please wait"

def renderWaitingPage():
    return render_template('waiting.html')
'''

if __name__ == '__main__':
    app.run(debug=True, ssl_context=('cert.pem', 'private_key.pem'), host='192.168.172.120', port=5000)


