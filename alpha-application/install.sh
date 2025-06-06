#!/bin/bash
set -e
set -v

# Create virtual environment and install libraries
cd /home/vagrant/oauth-site/
sudo apt update
sudo apt install python3-pip python3.10-venv -y
python3 -m venv venv
bash -c "source /home/vagrant/oauth-site/venv/bin/activate"
pip install -r /home/vagrant/oauth-site/requirements.txt

# Generate an HTTPS certificate
openssl req -new -newkey rsa:4096 -nodes -keyout /home/vagrant/oauth-site/private_key.pem -out /home/vagrant/oauth-site/csr.pem -subj "/C=US/ST=Illinois/L=Chicago/O=IIT/CN=iit.edu"
openssl x509 -req -in /home/vagrant/oauth-site/csr.pem -signkey /home/vagrant/oauth-site/private_key.pem -out /home/vagrant/oauth-site/cert.pem

# Start the flask server
# python3 /home/vagrant/oauth-site/app.py
