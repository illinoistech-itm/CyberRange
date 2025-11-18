#!/bin/bash

############################################################################################
# Script to install all the pre-reqs needed to instantiate pyxtermjs 
#############################################################################################

sudo apt install pipx -y
pipx install pyxtermjs
pipx ensurepath 
sudo apt install python3-eventlet -y
