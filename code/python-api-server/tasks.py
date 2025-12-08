from celery import Celery
from fabric import Connection
import redis
import time
import os
import json
import logging
from systemd.journal import JournalHandler
# Import Python3 Fabric library for SSH connection to buildserver
from fabric import Connection
from paramiko import AutoAddPolicy
import hvac
from dotenv import load_dotenv

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
VAULT_TOKEN = creds['data']['data']['APP_VAULTTOKEN']
vault_token_build_server = creds['data']['data']['APP_VAULTTOKEN']
vault_addr_build_server = 'https://jrh-vault-instance-vm0.service.consul:8200'
vault_skip_verify_build_server = "true"

celery = Celery("tasks", broker="redis://localhost:6379/", backend="redis://localhost:6379/")
r = redis.Redis()

def update_progress(task_id, status, output=""):
    logger.info("About to run function update_progress defined...")
    data = { "status": status, "output": output, "timestamp": str(time.time()) }
    r.set(f"progress:{task_id}", json.dumps(data) )

def get_task_progress(task_id):
    data = r.get(f"progress:{task_id}")
    return eval(data) if data else {"status": "PENDING", "output": "", "timestamp": 0}

@celery.task(bind=True)
def run_fabric_command(self, list_of_commands):
    logger.info("Running update_progress...")
    update_progress(self.request.id, "RUNNING", "Starting SSH command...")
    
    for cmd in list_of_commands:
        try:
            logger.info("About to run: " + cmd)
            result = conn.run(cmd, hide=True)
            update_progress(self.request.id, "RUNNING", "Running: " + cmd)
            if result.exited == 0:
              logger.info(cmd + " executed successfully (return 0)")
            else:
              logger.info(cmd + " failed with a return code of: {result.exited}")   
            
            update_progress(self.request.id, "SUCCESS", "Command completed: " + cmd)
            logger.info("success!!! for: " + cmd)
        
        except Exception as e:
            update_progress(self.request.id, "FAILURE", str(e))

    logger.info("Out of for loop and setting status to FINISHED...")
    update_progress(self.request.id, "FINISHED", "All commands completed.")
    logger.info("success!!! for " + cmd)
    