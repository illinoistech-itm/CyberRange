#!/bin/bash

##############################################################################
# Moving the private key used to connect to the build server, from the 
# location the Packer file provisioner copied the key to its destination 
# location so it can be used by the flask-api.service
##############################################################################
sudo mv /home/vagrant/id_ed25519_flask_api_to_buildserver_connect_key /home/flaskuser/
##############################################################################
# Change ownership of file so flask-api application, which is running as 
# flaskuser can access the SSH private key
##############################################################################
sudo chown flaskuser:flaskuser /home/flaskuser/id_ed25519_flask_api_to_buildserver_connect_key
