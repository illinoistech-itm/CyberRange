from flask import Flask, request, jsonify, session, Response
from flask_cors import CORS
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

# To communicate with Celery the task worker that lets us offload the long
# running SSH process to avoid the HTTP timeout
from tasks import run_fabric_command, get_task_progress


# Path to your ed25519 private key
ed25519_key_path = "/home/flaskuser/id_ed25519_flask_api_to_buildserver_connect_key"

HOST="newyorkphilharmonic.service.consul"
USER="cr"

# Create the connection
conn = Connection(
    host=HOST,
    user=USER,
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

# Needed to initialize the ability for Python to read from a .env file
load_dotenv()

# Initialize Vault client
client = hvac.Client(url=os.getenv('VAULTURL'), token=os.getenv('TOKEN'), verify=False)
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
VAULT_TOKEN = creds['data']['data']['APP_VAULTTOKEN']
FLASK_API_AC_KEY = creds['data']['data']['FLASK_API_AC_KEY']
FLASK_API_SEC_KEY = creds['data']['data']['FLASK_API_SEC_KEY']
vault_token_build_server = creds['data']['data']['APP_VAULTTOKEN']
vault_addr_build_server = os.getenv('VAULTURL')
vault_skip_verify_build_server = "true"

app = Flask(__name__)
app.secret_key = APP_SECRET
##############################################################################
# Restrict to your frontend origin?
##############################################################################
CORS(app, resources={r"/*": {"origins": ["https://system60.rice.iit.edu"]}}) 
##############################################################################

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
                            return runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address']
        
    if found42 == False:
        for vm in prxmx41:
            if vm['status'] == 'running' and str(launch_id) in vm['tags'] and 'edge' in vm['tags']:
                runningvms.append(vm)

                for vm in runningvms:
                    runningwithtagsvms.append(proxmox.nodes("system41").qemu(vm['vmid']).agent("network-get-interfaces").get())
                    for x in range(len(runningwithtagsvms)):
                            for y in range(len(runningwithtagsvms[x]['result'])):
                                if "192.168.172" in runningwithtagsvms[x]['result'][y]['ip-addresses'][0]['ip-address']:
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
# This route is more generic and will capture the commands and return one
# at a time -- making things easier to debug
##############################################################################
@app.route('/run', methods=['POST'])
def prepare_command():
    data = request.get_json()
    uid = data.get('runtime_uuid')
    email = data.get('email')
    lab_number = data.get('lab_number')
    username = email.split('@')[0] # the tags do not accept special characters, so we have to split out the '@' in the email address

    src = "/home/cr/CyberRange/build/terraform/proxmox-jammy-ubuntu-cr-lab-templates/" + lab_number
    dest = "/tmp/" + uid + "/"
    dest_after_copy = "/tmp/" + uid + "/" + lab_number
    t = uid + ";" + username + ";" + lab_number + ";" + "cr" + ";" + "edge"
    ln = uid + ";" + username + ";" + lab_number + ";" + "cr"
    # Gather all of the runtime terraform vars we will be assigning at terraform apply time
    vars = {
        "tags": t,
        "yourinitials": uid,
        "ln_yourinitials": uid,
        "ln_tags": ln
    }
    # Build the base command
    cmd = ["terraform", "apply", "-auto-approve"]

    # Append each -var argument
    for key, value in vars.items():
        cmd.append(f"-var '{key}={value}'") #syntax -var 'key=value'

    tf_cmd_str = " ".join(cmd)
    # Create strings of commands to send to the Celery worker tasks
    cmd_mkdir="mkdir -p " + dest
    cmd_cp="cp" + " -r " + src + " "  + dest
    cmd_tf_init="cd " + dest_after_copy + " && " + " terraform init"
    cmd_tf_apply = "cd " + dest_after_copy + "; VAULT_ADDR=" + vault_addr_build_server + " VAULT_TOKEN=" + vault_token_build_server +" VAULT_SKIP_VERIFY=" + vault_skip_verify_build_server + " " + tf_cmd_str
    list_of_commands = [cmd_mkdir,cmd_cp,cmd_tf_init,cmd_tf_apply]
    
    # Pass the constructed command to the Celery Task
    task = run_fabric_command.delay(list_of_commands)
    return jsonify({"task_id": task.id}), 202


@app.route("/status/<task_id>")
def status(task_id):
    progress = get_task_progress(task_id)
    return jsonify(progress)

@app.route("/stream/<task_id>")
def stream(task_id):
    def event_stream():
        last_sent = 0
        while True:
            progress = get_task_progress(task_id)
            if float(progress["timestamp"]) > last_sent:
                yield f"data: {progress}\n\n"
                last_sent = float(progress["timestamp"])
            if progress["status"] in ("SUCCESS", "FAILURE"):
                break
            time.sleep(1)
    return Response(event_stream(), mimetype="text/event-stream")

##############################################################################
# This route is more generic and will capture the commands and return one
# at a time -- making things easier to debug
##############################################################################
@app.route('/destroy', methods=['POST'])
def prepare_destroy_command():
    data = request.get_json()
    uid = data.get('runtime_uuid')
    email = data.get('email')
    lab_number = data.get('lab_number')
    username = email.split('@')[0] # the tags do not accept special characters, so we have to split out the '@' in the email address

    dest_after_copy = "/tmp/" + uid + "/" + lab_number
    t = uid + ";" + username + ";" + lab_number + ";" + "cr" + ";" + "edge"
    ln = uid + ";" + username + ";" + lab_number + ";" + "cr"
    # Gather all of the runtime terraform vars we will be assigning at terraform apply time
    vars = {
        "tags": t,
        "yourinitials": uid,
        "ln_yourinitials": uid,
        "ln_tags": ln
    }
    # Build the base command
    cmd = ["terraform", "destroy", "-auto-approve"]

    # Append each -var argument
    for key, value in vars.items():
        cmd.append(f"-var '{key}={value}'") #syntax -var 'key=value'

    tf_cmd_str = " ".join(cmd)
    # Create string of command to issue the terraform destroy to send to the Celery worker tasks
    cmd_tf_apply = "cd " + dest_after_copy + "; VAULT_ADDR=" + vault_addr_build_server + " VAULT_TOKEN=" + vault_token_build_server +" VAULT_SKIP_VERIFY=" + vault_skip_verify_build_server + " " + tf_cmd_str
    list_of_commands = [cmd_tf_apply]
    
    # Pass the constructed command to the Celery Task
    task = run_fabric_command.delay(list_of_commands)
    return jsonify({"task_id": task.id}), 202

##############################################################################
# Route to handle 404 errors
# https://copilot.microsoft.com/shares/sA2qT1ngFCwKdEwaExa4R
##############################################################################
@app.errorhandler(404)
def handle_404(e):
    
    print(e)                  # Outputs: 404 Not Found: The requested URL was not found on the server.
    print(e.code)             # 404
    print(e.name)             # 'Not Found'
    print(e.description)      # 'The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.'
    return jsonify(error='Resource not found'), 404
