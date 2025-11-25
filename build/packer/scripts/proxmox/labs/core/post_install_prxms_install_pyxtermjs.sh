#!/bin/bash

############################################################################################
# Script to install all the pre-reqs needed to instantiate pyxtermjs 
#############################################################################################

sudo apt install pipx -y
# sudo -u vagrant is to ensure that the packages are installed as vagrant not as root
sudo -u vagrant pipx install pyxtermjs
sudo -u vagrant pipx ensurepath 
sudo apt install python3-eventlet -y
