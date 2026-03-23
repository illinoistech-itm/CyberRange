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
frontend-yourinitials            = "cyberrange-fe"                     # initials to add to make unique systems
frontend-numberofvms             = 3                      # quantity of that template to launch
frontend-desc                    = "fe server for cyberrange ITMT 430 spring project"                     # What is the purpose of the TF template
backend-yourinitials             = "cyberrange-be"                     # initials to add to make unique systems
backend-numberofvms              = 2                      # quantity of that template to launch
backend-desc                     = "be server for cyberrange ITMT 430 spring project"                     # What is the purpose of the TF template
lb-yourinitials                  = "cyberrange-lb"                     # initials to add to make unique systems
lb-numberofvms                   = 1                      # quantity of that template to launch
lb-desc                          = "lb server for cyberrange ITMT 430 spring project"                     # What is the purpose of the TF template
logserver-yourinitials                  = "cyberrange-log"                     # initials to add to make unique systems
logserver-numberofvms                   = 1                      # quantity of that template to launch
logserver-desc                          = "log server for cyberrange ITMT 430 spring project"                     # What is the purpose of the TF template
lb-macaddr                       = "bc:24:11:00:00:53"                     # Class assigned mac address for a public IP for your lb
consul-service-tag-contact-email = "your-hawk-email-here" # Used as part of the consul service definition as a tag that can be queried
###############################################################################
# Name the template your created via Packer for Terraform to use to deploy
# instances from
###############################################################################
frontend-template_to_clone = "cyberrange-fe-template" # The name of the template to clone
backend-template_to_clone  = "cyberrange-be-template" # The name of the template to clone
lb-template_to_clone       = "cyberrange-lb-template" # The name of the template to clone
logserver-template_to_clone = "cyberrange-logs-template" # The name of the template to clone
fe-tags                    = "cr, frontend" # Tags separated by commas: fe,team00
lb-tags                    = "cr, loadbalancer" # Tags separated by commas: lb,team00
be-tags                    = "cr, backend" # Tags separated by commas: be,team00
ls-tags                    = "cr, loki" # Tags separated by commas: ls,team00
###############################################################################
# Customize instance hardware settings
###############################################################################
frontend-memory    = 2048  # Memory size of a VM
frontend-cores     = 1     # vCPU = cores * sockets
frontend-sockets   = 1     # vCPU = cores * sockets
frontend-disk_size = "30G" # Disk size of a VM - min size must equal to the disk size of your clone image
backend-memory     = 2048  # Memory size of a VM
backend-cores      = 1     # vCPU = cores * sockets
backend-sockets    = 1     # vCPU = cores * sockets
backend-disk_size  = "30G" # Disk size of a VM - min size must equal to the disk size of your clone image
lb-memory          = 2048  # Memory size of a VM
lb-cores           = 1     # vCPU = cores * sockets
lb-sockets         = 1     # vCPU = cores * sockets
lb-disk_size       = "30G" # Disk size of a VM - min size must equal to the disk size of your clone image
logserver-memory          = 2048  # Memory size of a VM
logserver-cores           = 1     # vCPU = cores * sockets
logserver-sockets         = 1     # vCPU = cores * sockets
logserver-disk_size       = "30G" # Disk size of a VM - min size must equal to the disk size of your clone image