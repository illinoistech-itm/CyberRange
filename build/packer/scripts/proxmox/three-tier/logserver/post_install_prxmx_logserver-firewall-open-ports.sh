#!/bin/bash
# Configure 3100 port open to receive systemd logs

sudo firewall-cmd --zone=meta-network --add-port=3100/tcp --permanent
sudo firewall-cmd --zone=meta-network --add-service=ssh --permanent

sudo firewall-cmd --reload
