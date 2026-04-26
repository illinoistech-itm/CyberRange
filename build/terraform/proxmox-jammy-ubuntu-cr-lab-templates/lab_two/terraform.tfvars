###############################################################################
# These are your proxmox API token credentials (not username and password)
# That will be provided to you
###############################################################################
keypath = "id_ed25519_cr_connect_key" # The name to the private key you need to communicate with your instances
###############################################################################
# Debugging information settings
# No need to change these values
###############################################################################
pm_log_enable = true                           # Optional; defaults to false) Enable debug logging, see the section below for logging details
pm_parallel   = 2                              # (Optional; defaults to 4) Allowed simultaneous Proxmox processes (e.g. creating resources).
pm_timeout    = 1600                           # (Optional; defaults to 300) Timeout value (seconds) for proxmox API calls.
pm_log_file   = "terraform-plugin-proxmox.log" # (Optional; defaults to terraform-plugin-proxmox.log) If logging is enabled, the log file the provider will write logs to.
###############################################################################
# This is a variable to append to your cloud instances so they have a unique
# FQDN -- this is needed for the gossip based DNS to work
###############################################################################
yourinitials                     = "cyberrange-lab-two-edge-server"         # Value needs to match the root URL of the FLASK_API_SERVER value you set in Vault
numberofvms                      = 1                      # quantity of that template to launch
desc                             = "Edge server for lab two"                     # What is the purpose of the TF template
ln_yourinitials                  = "cyberrange-lab-two-node"                     #
ln_numberofvms                   = 1                      # quantity of that template to launch
ln_desc                          = "Node for lab two"                     # What is the purpose of the TF template
consul-service-tag-contact-email = "your-hawk-email-here" # Used as part of the consul service definition as a tag that can be queried
###############################################################################
# Name the template your created via Packer for Terraform to use to deploy
# instances from
###############################################################################
template_to_clone = "cyberrange-lab-two-edge-server-template" # The name of the template to clone
ln_template_to_clone = "cyberrange-lab-two-node-template" # The name of the template to clone
ln_tags = "cr,lab_two" # Tags separated by commas: be,team00
tags = "cr, lab_two,edge" # Tags separated by commas: be,team00
###############################################################################
# Customize instance hardware settings
###############################################################################
memory    = 4096  # Memory size of a VM
cores     = 1     # vCPU = cores * sockets
sockets   = 1     # vCPU = cores * sockets
disk_size = "30G" # Disk size of a VM - min size must equal to the disk size of your clone image
