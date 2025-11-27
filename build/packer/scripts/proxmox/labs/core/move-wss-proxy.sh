#!/bin/bash

sudo mv /home/vagrant/wss-proxy.service /etc/systemd/system/

sudo systemctl enable wss-proxy.service
