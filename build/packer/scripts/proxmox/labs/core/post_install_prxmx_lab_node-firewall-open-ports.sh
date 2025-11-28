#!/bin/bash

sudo firewall-cmd --zone=public --add-service=https --permanent
sudo firewall-cmd --zone=public --add-port=5000/tcp --permanent

sudo firewall-cmd --reload
