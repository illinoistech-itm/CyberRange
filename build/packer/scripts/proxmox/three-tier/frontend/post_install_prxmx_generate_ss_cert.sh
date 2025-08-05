#!/bin/bash

# Generate a self-signed Certificate

# https://stackoverflow.com/questions/10175812/how-to-create-a-self-signed-certificate-with-openssl
# https://ethitter.com/2016/05/generating-a-csr-with-san-at-the-command-line/
sudo openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout /home/flaskuser/selfsigned.key -out /home/flaskuser/selfsigned.crt -subj "/C=US/ST=IL/L=Chicago/O=IIT/OU=rice/CN=iit.edu"
sudo chown flaskuser:flaskuser /home/flaskuser/selfsigned.key
sudo chown flaskuser:flaskuser /home/flaskuser/selfsigned.crt
