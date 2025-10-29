#!/bin/bash

# https://4sysops.com/archives/install-and-use-the-step-ca-certificate-authority-client/
# https://4sysops.com/archives/step-ca-running-your-own-certificate-authority-with-acme-support/

# installing step-cli 
wget https://dl.smallstep.com/cli/docs-cli-install/latest/step-cli_amd64.deb
sudo dpkg -i step-cli_amd64.deb

# have to find a way to dynamically get the password and fingerprint from the CA server
sudo step ca bootstrap --ca-url https://system36.rice.iit.edu --fingerprint 095ecc2996e06e9c84d4d1ff211fefb545e4097a3cde68249ecb04cfe231a1b7
sudo step certificate install --all /etc/step-ca/certs/root_ca.crt
