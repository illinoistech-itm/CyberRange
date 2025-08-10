from flask import Flask, request, jsonify
import hvac
from dotenv import load_dotenv
import os, re, time, subprocess
from proxmoxer import ProxmoxAPI
# Needed for local SQLite logging of requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# How to add Request logging to SQLite3 instance
# https://copilot.microsoft.com/shares/gw1pHzhN4AKzFNGNE8YpH
load_dotenv()
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

# Retrieve Proxmox Token connection to execute terraform apply
# Added by JRH
CR_TOKEN_ID = creds['data']['data']['CR_TOKEN_ID']
CR_TOKEN_VALUE = creds['data']['data']['CR_TOKEN_VALUE']
CR_PROXMOX_URL = creds['data']['data']['CR_PROXMOX_URL']

app = Flask(__name__)
# Initializing SQLite3 with SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///request_logs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create a model to store request metadata:
class RequestLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(10))
    path = db.Column(db.String(200))
    headers = db.Column(db.Text)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

with app.app_context():
    db.create_all()
##############################################################################
# Flask-api setup
##############################################################################
##############################################################################
# This will capture each request and log it for future review
##############################################################################
@app.before_request
def log_request():
    log = RequestLog(
        method=request.method,
        path=request.path,
        headers=str(dict(request.headers)),
        body=request.get_data(as_text=True)
    )
    db.session.add(log)
    db.session.commit()

##############################################################################
# This route capture the request from the CR Dashboard
##############################################################################
@app.route('/run', methods=['POST'])
def run_command():
    data = request.get_json()
    command = data.get('command')

    if not command:
        return jsonify({'error': 'No command provided'}), 400

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

##############################################################################
# Route to handle 404 errors
# https://copilot.microsoft.com/shares/sA2qT1ngFCwKdEwaExa4R
##############################################################################
@app.errorhandler(404)
def handle_404(e):
    return jsonify(error='Resource not found'), 404

    print(e)                  # Outputs: 404 Not Found: The requested URL was not found on the server.
    print(e.code)             # 404
    print(e.name)             # 'Not Found'
    print(e.description)      # 'The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.'
