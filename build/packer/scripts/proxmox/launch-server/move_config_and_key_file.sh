# Move config and key files to their respective directories to be used by the Flask API server and for GitHub access
# cr user needs read access to the config and key files to be able to run the Flask API server and clone the private GitHub repo
mv /home/vagrant/.ssh/config /home/cr/.ssh/config
chmod 644 /home/cr/.ssh/config
mv /home/vagrant/.ssh/id_ed25519_github_key /home/cr/.ssh/id_ed25519_github_key
chmod 600 /home/cr/.ssh/id_ed25519_github_key