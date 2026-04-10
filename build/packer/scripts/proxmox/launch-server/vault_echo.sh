#!/bin/bash
echo "export VAULT_ADDR='https://cyberrange-vault-vm0.service.consul:8200'" | sudo tee -a /home/cr/.bashrc
echo "export VAULT_SKIP_VERIFY=true" | sudo tee -a /home/cr/.bashrc


## Needed for CR user to talk to vault in order to terraform apply, utilizing API keys ##

