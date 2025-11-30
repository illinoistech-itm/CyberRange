#!/bin/bash 
set -e
set -v

# https://copilot.microsoft.com/shares/Pxz7LVbyQtyLZ4on86zkM

echo "Create system account and group flaskuser ..."
sudo adduser --system --group flaskuser

# https://copilot.microsoft.com/shares/nis5fbJZkaup7K34PRKwK

#sudo mv /home/vagrant/CyberRange/code/lab-core/app.py /home/flaskuser/app.py
#sudo mv /home/vagrant/CyberRange/code/python-flask/labs /home/flaskuser/labs

sudo chown -R flaskuser:flaskuser /home/flaskuser/app.py
