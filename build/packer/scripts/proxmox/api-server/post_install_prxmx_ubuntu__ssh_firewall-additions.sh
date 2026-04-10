#!/bin/bash 
set -e
set -v

##############################################################################################
# Add any additional firewall ports below this line in this format:
# sudo firewall-cmd --zone=public --add-port=####/tcp --permanent
# sudo firewall-cmd --zone=public --add-port=####/udp --permanent
##############################################################################################
# Open port 22 on the internal meta-network and public zones for SSH access
sudo firewall-cmd --zone=meta-network --add-service=ssh --permanent

# Restart the firewall to reload the rules
sudo firewall-cmd --reload
