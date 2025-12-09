#!/bin/bash

sudo apt update
sudo apt install -y ca-certificates

# Copy root cert to certificate store
sudo mv /home/vagrant/root_ca.crt /usr/local/share/ca-certificates/root_ca.crt

# Update certificate store
sudo update-ca-certificates
