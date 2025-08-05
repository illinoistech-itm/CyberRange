from flask import Flask, request, redirect, url_for, session, render_template
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
import hvac
from dotenv import load_dotenv
import os

load_dotenv()

####Verified working with Vault#####

# Initialize Vault client
client = hvac.Client(url='https://jrh-vault-instance-vm0.service.consul:8200', token=os.getenv('TOKEN'), verify=False)
# Added Verify=False, remove hardcoded token for production use


# Check authentication
assert client.is_authenticated()

# Read dynamic MySQL credentials from Vault
creds = client.read('secret/data/CR')

# Extract username and password
CLIENT_ID = creds['data']['data']['CLIENT_ID']
CLIENT_SECRET = creds['data']['data']['CLIENT_SECRET']
APP_SECRET = creds['data']['data']['APP_SECRET']




app = Flask(__name__)
########################################3
# Flask-Login setup
app.secret_key = 'APP_SECRET' # Change to point to the vault instance EDIT: Added Manually, add back as 'APP_SECRET'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OAuth configuration
client_id = 'CLIENT_ID' #Added Manually for Debugging, add back as 'CLIENT_ID'
client_secret = 'CLIENT_SECRET' #Added Manually, add back as 'CLIENT_SECRET'
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

@app.route("/test")
def hello_world():
    return "<p>Hello, Cyber Range!</p>"


