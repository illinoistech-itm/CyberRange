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
from systemd.journal import JournalHandler
# Import Python3 Fabric library for SSH connection to buildserver
from fabric import Connection
from paramiko import AutoAddPolicy

# Path to your ed25519 private key
ed25519_key_path = "/home/flaskuser/id_ed25519_flask_api_to_buildserver_connect_key"

# Create the connection
conn = Connection(
    host="newyorkphilharmonic.service.consul",
    user="cr",
    connect_kwargs={
        "key_filename": ed25519_key_path,
    }
)

# Initialize no strict host key checking
conn.client.set_missing_host_key_policy(AutoAddPolicy())

# Initialize logging object to send logs to the journal
logger = logging.getLogger('cyberrange')
journald_handler = JournalHandler()
journald_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger.addHandler(journald_handler)
logger.setLevel(logging.INFO)

# Needed to initialze the ability for Python to read from a .env file
load_dotenv()

# Initialize Vault client
client = hvac.Client(url='https://jrh-vault-instance-vm0.service.consul:8200', token=os.getenv('TOKEN'), verify=False)
# Added Verify=False, remove hardcoded token for production use

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
vault_token_build_server = creds['data']['data']['APP_VAULTTOKEN']
vault_addr_build_server = 'https://jrh-vault-instance-vm0.service.consul:8200'
vault_skip_verify_build_server = "true"

app = Flask(__name__)
app.secret_key = APP_SECRET

##############################################################################
# Proxmoxer Helper function
##############################################################################
@app.route('/getip', methods=['POST'])
def run_getip():
    data = request.get_json()
    session['runtime_uuid'] = data.get('runtime_uuid')
    email = data.get('email')
    username = email.split('@')[0] # the tags do not accept special characters, so we have to split the email address
    lab_number = data.get('lab_number')
    TOKEN = CR_TOKEN_ID.split('!')
    proxmox = ProxmoxAPI(CR_PROXMOX_URL, user=TOKEN[0], token_name=TOKEN[1], token_value=CR_TOKEN_VALUE, verify_ssl=False)

    prxmx42 = proxmox.nodes("system42").qemu.get()

    runningvms = []
    runningwithtagsvms = []
    # Loop through the first node to get all of the nodes that are of status 
    # running and that have the tag of the user for vm in prxmx42:
    for vm in prxmx42:
        if vm['status'] == 'running' and vm['tags'].split(';')[0] == session['runtime_uuid']:
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
    username = email.split('@')[0] # the tags do not accept special characters, so we have to split the email address
    lab_number = data.get('lab_number')
    src = "/home/cr/CyberRange/build/terraform/proxmox-jammy-ubuntu-cr-lab-templates/" + lab_number
    dest = "/tmp/" + session['runtime_uuid'] + "/"
    dest_after_copy = "/tmp/" + session['runtime_uuid'] + "/" + lab_number
    t = session['runtime_uuid'] + ";" + username + ";" + lab_number + ";" + "cr"
    logger.info("Data from received HTTP post...", extra={
    'USER': 'cr',
    'STATUS': 'success',
    'VALUE': data
    })

    # Command to copy the original Terraform plan to a tmp location 
    # (need to store this in session) so it can be retrieved later...
    # Navigate to the Terraform directory and apply
    try:
        logger.info("About to run: mkdir -p " + dest + " ::the mkdir command to create a new directory for the terraform plan files...")
        result_mkdir = conn.run("mkdir -p " + dest, hide=True)
        if result_mkdir.exited == 0:
          logger.info("mkdir -p " + dest + " executed successfully (return 0)")
        else:
          logger.info(f"mkdir -p " + dest + " failed with a return code of: {result_mkdir.exited}")
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    try:
        logger.info("About to run: cp -r " + src + " "  + dest)
        result_cp = conn.run("cp" + " -r " + src + " "  + dest, hide=True)
        if result_cp.exited == 0:
          logger.info("cp -r " + src + " "  + dest + " executed successfully (return 0)")
        else:
          logger.info(f"cp -r " + src + " "  + dest + " failed with a return code of: {result_cp.exited}")
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
      
    try:
        logger.info("What directory are we running tf init? " + dest_after_copy)
        result_tf_init = conn.run("cd " + dest_after_copy + " && " + "terraform init", hide=True) # need to append dest lab_one
        if result_tf_init.exited == 0:
            logger.info("cd " + dest_after_copy + " && " + "terraform init executed successfully (return 0)")
        else:
            logger.info(f"cd {dest_after_copy} && terraform init failed with a return code of: {result_tf_init.exited}")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    try:    
        # Gather all of the runtime terraform vars we will be assigning at terraform apply time
        vars = {
            "tags": t,
            "yourinitials": session['runtime_uuid']
        }

        # Build the base command
        cmd = ["terraform", "apply", "-auto-approve"]

        # Append each -var argument
        for key, value in vars.items():
            cmd.append(f"-var '{key}={value}'") #syntax -var 'key=value'

        tf_cmd_str = " ".join(cmd)
        logger.info(f"Constructing the Terraform command...")
        logger.info(f"About to run: cd {dest_after_copy} ; VAULT_ADDR={vault_addr_build_server} VAULT_TOKEN={vault_token_build_server} VAULT_SKIP_VERIFIY={vault_skip_verify_build_server} {tf_cmd_str}")
        result_cd_tfapply = conn.run(f"cd {dest_after_copy} ; VAULT_ADDR={vault_addr_build_server} VAULT_TOKEN={vault_token_build_server} VAULT_SKIP_VERIFIY={vault_skip_verify_build_server} {tf_cmd_str}", pty=True, hide=False)
        if result_cd_tfapply.exited == 0:
            logger.info(f"cd {dest_after_copy} ; VAULT_ADDR={vault_addr_build_server} VAULT_TOKEN={vault_token_build_server} VAULT_SKIP_VERIFIY={vault_skip_verify_build_server} {tf_cmd_str}" + " executed successfully (return 0)")
        else:
            logger.info(f"cd {dest_after_copy} ; VAULT_ADDR={vault_addr_build_server} VAULT_TOKEN={vault_token_build_server} VAULT_SKIP_VERIFIY={vault_skip_verify_build_server} {tf_cmd_str} failed with a return code of: {result_cd_tfapply.exited}")
    except Exception as e:
        return jsonify({'error': str(e)}), 500    
    
    # If everything executes successfully return 1
    return 1
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
