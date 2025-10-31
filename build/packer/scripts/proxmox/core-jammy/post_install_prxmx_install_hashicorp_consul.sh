#!/bin/bash

# script to install hashicorp consul for Proxmox servers

wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install consul

sudo systemctl stop consul.service
sudo mv -v /home/vagrant/system.hcl /etc/consul.d/
sudo mv -v /home/vagrant/node-exporter-consul-service.json /etc/consul.d/
sudo systemctl enable consul.service
