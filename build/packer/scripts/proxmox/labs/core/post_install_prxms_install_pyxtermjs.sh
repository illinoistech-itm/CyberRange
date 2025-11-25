#!/bin/bash

############################################################################################
# Script to install all the pre-reqs needed to instantiate pyxtermjs 
#############################################################################################

sudo apt install pipx -y
# sudo -u vagrant is to ensure that the packages are installed as vagrant not as root
sudo -u flaskuser pipx install pyxtermjs
sudo -u flaskuser pipx ensurepath 
