#!/bin/bash 
set -e
set -v

# https://copilot.microsoft.com/shares/Pxz7LVbyQtyLZ4on86zkM

echo "Create system account and group flaskuser ..."
sudo adduser --system --group flaskuser

# https://copilot.microsoft.com/shares/nis5fbJZkaup7K34PRKwK

sudo mv /home/vagrant/CyberRange/code/python-flask/app.py /home/flaskuser/app.py
sudo mv /home/vagrant/CyberRange/code/python-flask/.env /home/flaskuser/.env
# Move private key that will be needed to connect to the edge_nodes
sudo mv /home/vagrant/.ssh/id_ed25519_paramiko_connect_key_from_flask_app_to_lab_edge_node /home/flaskuser/id_ed25519_paramiko_connect_key_from_flask_app_to_lab_edge_node
sudo mv /home/vagrant/CyberRange/code/python-flask/static/ /home/flaskuser/static/
sudo mv /home/vagrant/CyberRange/code/python-flask/templates/ /home/flaskuser/templates/
# Move all the lab question and answer files over
sudo mv /home/vagrant/CyberRange/code/python-flask/labs/ /home/flaskuser/labs/

# How to use an ENV variable in a sed command
# https://askubuntu.com/questions/76808/how-do-i-use-variables-in-a-sed-command
sed -i "s/REPLACE/$APPVAULT_TOKEN/g" /home/flaskuser/.env
sudo chown -R flaskuser:flaskuser /home/flaskuser/*
