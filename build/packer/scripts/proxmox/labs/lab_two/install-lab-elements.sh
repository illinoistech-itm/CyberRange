#!/bin/bash

# Just a simple script to install and configure the elements of the lab
sudo apt update

sudo apt install -y mariadb-server

# Open database to listen externally
sudo sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/mariadb.conf.d/50-server.cnf

sudo systemctl enable mariadb.service
