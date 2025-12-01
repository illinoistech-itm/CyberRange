#!/bin/bash

# Generate a signed certificate 

# https://4sysops.com/archives/install-and-use-the-step-ca-certificate-authority-client/
# https://4sysops.com/archives/step-ca-running-your-own-certificate-authority-with-acme-support/

# installing step-cli 
wget https://dl.smallstep.com/cli/docs-cli-install/latest/step-cli_amd64.deb
sudo dpkg -i step-cli_amd64.deb

# have to find a way to dynamically get the password and fingerprint from the CA server
#sudo step ca bootstrap --ca-url https://system36.rice.iit.edu --fingerprint 095ecc2996e06e9c84d4d1ff211fefb545e4097a3cde68249ecb04cfe231a1b7 
#sudo step ca bootstrap --ca-url https://system36.rice.iit.edu --fingerprint 81834205d8387947c53adb24a4ca6f6eca1c54e7602f30ebfd584cae62cc9c4c
sudo step ca bootstrap --ca-url https://system36.rice.iit.edu --fingerprint $FINGERPRINT
#sudo step certificate install --all /etc/step-ca/certs/root_ca.crt
sudo step certificate install --all /root/.step/certs/root_ca.crt
#echo "158234246165263303871269841982826793299" > password.txt <--commented out to test alternative, add back in if fails
echo "176820514074201284967811592992451421160" > provisioner-password.txt

# explaining the flags https://smallstep.com/docs/step-cli/reference/ca/token/
#TOKEN=$(sudo step ca token system36.rice.iit.edu --ca-url=system36.rice.iit.edu --provisioner-password-file=password.txt --root=/etc/step-ca/certs/root_ca.crt --kid=2lK2ZHwu-0wqHlrK6YflrcELu9WkaF8T7CDvu-NQwGs)
# 8544 hours is 1 year in hours
TOKEN=$(sudo step ca token system57.rice.iit.edu \
 --ca-url=system36.rice.iit.edu \
 --provisioner-password-file provisioner-password.txt \
 --provisioner "vagrant@system36.rice.iit.edu" \
 --root /root/.step/certs/root_ca.crt \
 --kid _NDDiuYtkkyRQMDb9b4jPw0alz_3SG5z5STPYdRfOjI)

#check if token generation was successful
if [ -z "$TOKEN" ]; then
    echo "Error: Failed to generate token"
    exit 1
fi

echo "Token generated successfully"


#sudo step ca certificate --token $TOKEN system36.rice.iit.edu CAcr.crt CAcr.key <---commented out to test alternative, add back in if fails
sudo step ca certificate system57.rice.iit.edu \
    CAcr.crt \
    CAcr.key \
    --token "$TOKEN" \
    --ca-url https://system36.rice.iit.edu \
    --root /root/.step/certs/root_ca.crt \
    --not-after=8760h 

# Check if files were created successfully
if [ ! -f "CAcr.crt" ] || [ ! -f "CAcr.key" ]; then
    echo "Error: Certificate files were not created"
    exit 1
fi

# Move the generated files to the flaskuser's home directory
sudo mv CAcr.crt /home/flaskuser/ || { echo "Failed to move cert"; exit 1; }
sudo mv CAcr.key /home/flaskuser/ || { echo "Failed to move key"; exit 1; }

sudo chown flaskuser:flaskuser /home/flaskuser/CAcr.crt
sudo chown flaskuser:flaskuser /home/flaskuser/CAcr.key
sudo chmod 600 /home/flaskuser/CAcr.crt
sudo chmod 600 /home/flaskuser/CAcr.key
sudo chmod 600 provisioner-password.txt

echo "Certificate and unencrypted key successfully created"
