#!/bin/bash 
set -e
set -v

##############################################################################################
# Add any additional firewall ports below this line in this format:
# sudo firewall-cmd --zone=public --add-port=####/tcp --permanent
# sudo firewall-cmd --zone=public --add-port=####/udp --permanent
##############################################################################################
# Open port 3000 on the internal meta-network port 3000 for our Flask App
sudo firewall-cmd --zone=meta-network --add-port=3000/tcp --permanent

# Restart the firewall to reload the rules
sudo firewall-cmd --reload
