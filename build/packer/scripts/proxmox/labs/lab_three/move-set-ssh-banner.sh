#!/bin/bash

# script to move the set-ssh-banner.cond into the /etc/ssh/sshd_config.d/ dir

sudo mv /home/vagrant/set-ssh-banner.conf /etc/ssh/sshd_config.d/
sudo mv /home/vagrant/sshd-banner /etc/ssh