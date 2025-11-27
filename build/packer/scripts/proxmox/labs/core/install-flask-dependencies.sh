#!/bin/bash

sudo apt install -y python3-flask python3-flask-socketio

# Dependencies for the wss-proxy.service -- we are not running this via pipx that is only for the 
# pyxtermjs which we will install/inject dependencies via pipx...  python...

sudo apt install -y python3-dev gunicorn python3-gevent
