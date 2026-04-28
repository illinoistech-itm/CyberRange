#!/bin/bash

#############################################################################
# Using the file provisioner to SCP the timer and service file into the
# virtual machine so that the service to renew the cert each week takes 
# place
#############################################################################

echo "Moving ./renew-cert.timer..."
sudo mv -v /home/vagrant/renew-cert.timer /etc/systemd/system/

echo "Moving ./renew-cert.service..."
sudo mv -v /home/vagrant/renew-cert.service /etc/systemd/system/

echo "Enabling timer service to renew cert every Tuesday at 4am..."
sudo systemctl enable renew-cert.timer
