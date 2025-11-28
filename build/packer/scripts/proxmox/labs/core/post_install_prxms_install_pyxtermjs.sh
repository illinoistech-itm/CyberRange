#!/bin/bash

############################################################################################
# Script to install all the pre-reqs needed to instantiate pyxtermjs 
#############################################################################################

sudo apt install pipx -y
# sudo -u vagrant is to ensure that the packages are installed as vagrant not as root
# Need to inject each package into the others virtual environment otherwise you will
# receive a module not found error
sudo -u flaskuser pipx install pyxtermjs
sudo -u flaskuser pipx install gunicorn
sudo -u flaskuser pipx inject pyxtermjs gunicorn eventlet gevent
sudo -u flaskuser pipx inject gunicorn pyxtermjs eventlet gevent

# Using sed to replace the app instantiation and wrap it in a CORS allow Origin for system60
sudo sed -i 's/socketio = SocketIO(app)/socketio = SocketIO(app, cors_allowed_origins="https\:\/\/system60.rice.iit.edu")/g' /home/flaskuser/.local/pipx/venvs/pyxtermjs/lib/python3.10/site-packages/pyxtermjs/app.py
sudo sed -i 's/socketio = SocketIO(app)/socketio = SocketIO(app, cors_allowed_origins="https\:\/\/system60.rice.iit.edu")/g' /home/flaskuser/.local/pipx/venvs/gunicorn/lib/python3.10/site-packages/pyxtermjs/app.py
