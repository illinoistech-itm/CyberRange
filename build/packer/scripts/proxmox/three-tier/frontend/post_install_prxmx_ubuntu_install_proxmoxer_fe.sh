#!/bin/bash

#Script to install proxmoxer library
# https://pypi.org/project/proxmoxer/
#Proxmoxer is a python wrapper around the Proxmox REST API v2. It currently supports the Proxmox services of Proxmox Virtual Environment (PVE), Proxmox Mail Gateway (PMG), and Proxmox Backup Server (PBS).
#It was inspired by slumber, but it is dedicated only to Proxmox. It allows not only REST API use over HTTPS, but the same api over ssh and pvesh utility.
#Like Proxmoxia, it dynamically creates attributes which responds to the attributes you’ve attempted to reach.

sudo apt update

sudo apt install -y python3-proxmoxer
