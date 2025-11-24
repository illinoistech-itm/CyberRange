#!/bin/bash

# Need to install nginx as a proxy for the internal pyxtermjs listening on 5000
# Proxy through 443

sudo apt update

sudo apt install -y nginx

sudo systemctl enable nginx
