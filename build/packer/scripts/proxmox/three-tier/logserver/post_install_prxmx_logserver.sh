#!/bin/bash

sudo apt update

sudo apt install -y logcli loki

sudo mv /home/vagrant/config.yml /etc/loki

sudo systemctl enable loki.service
