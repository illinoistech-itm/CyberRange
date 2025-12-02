#!/bin/bash

# Just a simple script to install and configure the elements of the lab
sudo apt update

sudo apt install -y mariadb

sudo systemctl enable mariadb
