#!/bin/bash

# following the https://4sysops.com/archives/step-ca-running-your-own-certificate-authority-with-acme-support/
# tutorial for creating our own CA authority

# updating and upgrading system
sudo apt -y update
sudo apt -y upgrade
sudo apt -y install wget
wget https://dl.smallstep.com/certificates/docs-ca-install/latest/step-ca_amd64.deb

# installing step-ca and step-cli
sudo dpkg -i step-ca_amd64.deb
wget https://dl.smallstep.com/cli/docs-ca-install/latest/step-cli_amd64.deb
sudo dpkg -i step-cli_amd64.deb

# create password.txt to pass through in the init command
uuid -F SIV -o password.txt

# initializing step-ca 
# have to pass through variables
step ca init --deployment-type=standalone --name=CyberRangeCA --dns=system36.rice.iit.edu --address=:443 --provisioner=vagrant@system36.rice.iit.edu --password-file=password.txt

# adding ACME provisioner support
step ca provisioner add acme --type ACME

# running step-ca as a regular user and starting the server 
sudo setcap CAP_NET_BIND_SERVICE=+eip $(which step-ca)
step-ca --password-file ./password.txt

# locking down the password file
sudo chmod 600 password.txt



