#!/bin/bash

sudo firewall-cmd --zone=meta-network --add-port=3001/tcp --permanent
sudo firewall-cmd --zone=meta-network --add-service=ssh --permanent

sudo firewall-cmd --reload
