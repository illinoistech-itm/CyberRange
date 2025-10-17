#!/bin/bash

# Generate a signed certificate 

# https://4sysops.com/archives/install-and-use-the-step-ca-certificate-authority-client/
# https://4sysops.com/archives/step-ca-running-your-own-certificate-authority-with-acme-support/

# have to find a way to dynamically get the password and fingerprint from the CA server
sudo step ca bootstrap --ca-url https://system36.rice.iit.edu --fingerprint f230790d390351b320c22adace7ad894eef3a94e79c17385f07956e8264267fc
sudo step certificate install --all ~/.step/certs/root_ca.crt
sudo TOKEN=$(step ca token system36.rice.iit.edu --provisioner-password 'aaS9UoZFnEfpECJI3dEgJtzHM6Q6W1xK') # find how to pass through the password
sudo step ca certificate --token $TOKEN system36.rice.iit.edu CAcr.crt CAcr.key
