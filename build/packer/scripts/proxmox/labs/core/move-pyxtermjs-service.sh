#!/bin/bash

sudo mv /home/vagrant/pyxtermjs.service /etc/systemd/system

sudo systemctl enable pyxtermjs.service
