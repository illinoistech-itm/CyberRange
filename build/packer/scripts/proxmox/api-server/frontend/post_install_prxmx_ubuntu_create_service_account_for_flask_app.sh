#!/bin/bash 
set -e
set -v

# https://copilot.microsoft.com/shares/Pxz7LVbyQtyLZ4on86zkM

echo "Create system account and group flaskuser ..."
sudo adduser --system --group flaskuser

# https://copilot.microsoft.com/shares/nis5fbJZkaup7K34PRKwK

sudo mv /home/vagrant/CyberRange/code/python-api-server/app.py /home/flaskuser/app.py
sudo mv /home/vagrant/CyberRange/code/python-api-server/tasks.py /home/flaskuser/tasks.py
sudo mv /home/vagrant/CyberRange/code/python-api-server/.env /home/flaskuser/.env
# Copy directory with lab answers
sudo mv /home/vagrant/CyberRange/code/python-api-server/labs/ /home/flaskuser/labs/

# How to use an ENV variable in a sed command
# https://askubuntu.com/questions/76808/how-do-i-use-variables-in-a-sed-command
sed -i "s/REPLACE/$APPVAULT_TOKEN/g" /home/flaskuser/.env
sudo chown -R flaskuser:flaskuser /home/flaskuser/app.py
