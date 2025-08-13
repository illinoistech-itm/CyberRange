from flask import Flask, request, jsonify, session
import hvac
from dotenv import load_dotenv
import os, re, time, subprocess
from proxmoxer import ProxmoxAPI
# Needed for local SQLite logging of requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
# Import logging for keeping track requests
import logging
from systemd.journal import JournaldLogHandler
# Import Python3 Fabric library for SSH connection to buildserver
from fabric import Connection

# Path to your ed25519 private key
ed25519_key_path = "/home/flaskapp/id_ed25519_connect_to_buildserver_from_api_server"

# Create the connection
conn = Connection(
    host="newyorkphilharmonic.service.consul",
    user="cr",
    connect_kwargs={
        "key_filename": ed25519_key_path
        "allow_agent": False,
        "look_for_keys": False,
        "hostkey_policy": "AutoAddPolicy"  # Accept unknown host keys
    }
)

logger = logging.getLogger('cyberrange')
journald_handler = JournaldLogHandler()
journald_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger.addHandler(journald_handler)
logger.setLevel(logging.INFO)

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
# Python app secret to start session
APP_SECRET = creds['data']['data']['APP_SECRET']
CR_TOKEN_ID = creds['data']['data']['CR_TOKEN_ID']
CR_TOKEN_VALUE = creds['data']['data']['CR_TOKEN_VALUE']
CR_PROXMOX_URL = creds['data']['data']['CR_PROXMOX_URL']

app = Flask(__name__)
app.secret_key = 'APP_SECRET'

##############################################################################
# Proxmoxer Helper function
##############################################################################
def getip(UUID,tags,email):
    TOKEN = CR_TOKEN_ID.split('!')
    proxmox = ProxmoxAPI(CR_PROXMOX_URL, user=TOKEN[0], token_name=TOKEN[1], token_value=CR_TOKEN_VALUE, verify_ssl=False)

    prxmx42 = proxmox.nodes("system42").qemu.get()

    runningvms = []
    runningwithtagsvms = []
    # Loop through the first node to get all of the nodes that are of status 
    # running and that have the tag of the user for vm in prxmx42:
    if vm['status'] == 'running' and vm['tags'].split(';')[0] == UUID:
        runningvms.append(vm)

        for vm in runningvms:
            runningwithtagsvms.append(proxmox.nodes("system42").qemu(vm['vmid']).agent("network-get-interfaces").get())
            for x in range(len(runningwithtagsvms)):
                for y in range(len(runningwithtagsvms[x]['result'])):
                    if "192.168.100." in runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address']:
                        return runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address']
                        
        return None
##############################################################################
# Fabric SSH helper function
# This function uses Fabric on top of Paramiko in Python to make SSH 
# connections to remote system. In this case it will be the 'cr' account on 
# the buildserver to launch terraform plans.
##############################################################################
def create_and_run_copy_terraform_plan_command():

    return 1
##############################################################################
# This route capture the request from the CR Dashboard
##############################################################################
@app.route('/launch', methods=['POST'])
def run_launch_command():
    data = request.get_json()
    session['runtime_uuid'] = data.get('runtime_uuid')
    email = data.get('email')
    lab_number = data.get('lab_number')
    src = "/home/cr/CyberRange/build/terraform/proxmox-jammy-ubuntu-cr-lab-templates/lab_one/"
    dest = "/tmp/" + session['runtime_uuid'] + "/"
    working_dir = dest + session['runtime_uuid']
    t = session['runtime_uuid'] + ";" + email + ";" + "lab" + str(lab_number) + ";" + "cr"
    logger.info("Data from received HTTP post...", extra={
    'USER': 'cr',
    'STATUS': 'success',
    'VALUE': data
    })

    # Command to copy the original Terraform plan to a tmp location 
    # (need to store this in session) so it can be retrieved later...
    # Navigate to the Terraform directory and apply
    result_mkdir = conn.run("mkdir -p " + dest, hide=True)
    logger.info("Output running mkdir directory to create a new directory for this instance of the lab launch...", extra={
    'USER': 'cr',
    'VALUE': result_mkdir.stdout.strip()
    })
    result_cp = conn.run("cp" + " -r " + src + " "  + dest, hide=True)
    logger.info("Output running cp terraform plan command to new directory...", extra={
    'USER': 'cr',
    'VALUE': result_cp.stdout.strip()
    })
    
    try:
        vars = {
            "tags": t,
            "yourinitials": session['runtime_uuid']
        }

        # Build the base command
        cmd = ["terraform", "apply", "-auto-approve"]

        # Append each -var argument
        for key, value in vars.items():
            cmd.append(f"-var={key}={value}")
        
        logger.info("Terraform command about to run...", extra={    
        'USER': 'cr',
        'STATUS': 'pending',
        'VALUE': cmd
        })

        result_tfapply = conn.run("cd " + dest + " && " + cmd, hide=True)
        logger.info("Output running terraform apply command...", extra={
        'USER': 'cr',
        'VALUE': result_tfapply.stdout.strip()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

##############################################################################
# This route will launch or destroy the infrastructure for the declared lab 
# via terraform.
# We need to pass some runtime variables so we can retrieve the metadata
# later -- this will be done via Python3 Fabric/Invoke/Paramiko
##############################################################################
@app.route('/destroy', methods=['POST'])
def run_destroy_command():
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
# This route will use the Proxmoxer API wrapper to authenticate with our 
# Proxmox cluster and query and return the IP of the running edge_node for the
# SSH function
##############################################################################
@app.route('/getip', methods=['POST'])
def getip():
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
