#!/bin/bash

# https://4sysops.com/archives/install-and-use-the-step-ca-certificate-authority-client/
# https://4sysops.com/archives/step-ca-running-your-own-certificate-authority-with-acme-support/

# installing step-cli 
wget https://dl.smallstep.com/cli/docs-cli-install/latest/step-cli_amd64.deb
sudo dpkg -i step-cli_amd64.deb

# have to find a way to dynamically get the password and fingerprint from the CA server
sudo step ca bootstrap --ca-url https://system36.rice.iit.edu --fingerprint 81834205d8387947c53adb24a4ca6f6eca1c54e7602f30ebfd584cae62cc9c4c #Potentially adjust to use variable FINGERPRINT instead 
sudo step certificate install --all /root/.step/certs/root_ca.crt
