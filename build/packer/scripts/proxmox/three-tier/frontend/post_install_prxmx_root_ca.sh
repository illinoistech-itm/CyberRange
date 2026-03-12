#!/bin/bash

# https://4sysops.com/archives/install-and-use-the-step-ca-certificate-authority-client/
# https://4sysops.com/archives/step-ca-running-your-own-certificate-authority-with-acme-support/

# installing step-cli 
wget https://dl.smallstep.com/cli/docs-cli-install/latest/step-cli_amd64.deb
sudo dpkg -i step-cli_amd64.deb

# have to find a way to dynamically get the password and fingerprint from the CA server
sudo step ca bootstrap --ca-url https://system22h134.itm.iit.edu --fingerprint 21f95a2e578fe5c5b8247cc2c9cdb283119b04e9e3b0574a31d7fb6df7c81e6a #Potentially adjust to use variable FINGERPRINT instead 
sudo step certificate install --all /root/.step/certs/root_ca.crt
