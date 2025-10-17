#!/bin/bash

# following the https://4sysops.com/archives/step-ca-running-your-own-certificate-authority-with-acme-support/
# tutorial for creating our own CA authority
sudo mv /home/vagrant/step-ca.service /etc/systemd/system/step-ca.service

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

# running step-ca as a regular user(commented out starting step-ca to create it as a service)
sudo setcap CAP_NET_BIND_SERVICE=+eip $(which step-ca)
#step-ca --password-file ./password.txt

# steps to run step-ca as a service: running it under a service account, binding it to a port number <1024, 
sudo useradd --system --home /etc/step-ca --shell /bin/false step
sudo setcap CAP_NET_BIND_SERVICE=+eip $(which step-ca)

#moves it to step-ca system folder, changes owner to a user 'step'
sudo mkdir /etc/step-ca
sudo mv $(step path)/* /etc/step-ca
sudo cp /home/vagrant/password.txt /etc/step-ca/password.txt
sudo chown -R step:step /etc/step-ca

# enabling and starting the step-ca service
sudo systemctl daemon-reload
sudo systemctl enable --now step-ca
sudo systemctl status step-ca

echo "export STEPPATH=/etc/step-ca" >> /etc/profile

# locking down the password file
sudo chmod 600 /etc/step-ca/password.txt




