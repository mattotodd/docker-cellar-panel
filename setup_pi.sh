#!/bin/bash
#docker compose on raspberrypi
sudo apt update
sudo apt install -y \
     apt-transport-https \
     ca-certificates \
     curl \
     gnupg2 \
     software-properties-common
curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | sudo apt-key add -
echo "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
     $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt install -y --no-install-recommends \
    docker-ce \
    cgroupfs-mount
sudo systemctl enable docker
sudo systemctl start docker
sudo apt update
sudo apt install -y python3-pip libffi-dev
sudo pip3 install docker-compose
sudo gpasswd -a $USER docker
newgrp docker

sudo apt install git