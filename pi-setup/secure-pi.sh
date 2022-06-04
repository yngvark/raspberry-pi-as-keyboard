#!/usr/bin/env bash
# https://raspberrytips.com/security-tips-raspberry-pi/
HOST="pi@192.168.0.139"
PORT="1111"

ssh -t $HOST "sudo cp /etc/ssh/sshd_config /tmp"
ssh -t $HOST "sudo sed -i 's/#Port 22/#Port 22\nPort 1111/' /etc/ssh/sshd_config"
ssh -t $HOST "sudo service ssh restart"

ssh -t $HOST -p $PORT "sudo apt install -y unattended-upgrades"
ssh -t $HOST -p $PORT "mkdir -p /tmp/secure-pi"

scp 02periodic $HOST:/tmp/secure-pi
ssh -t $HOST -p $PORT "sudo chown root:root /tmp/secure-pi/02periodic"
ssh -t $HOST -p $PORT "sudo mv /tmp/secure-pi/02periodic /etc/apt/apt.conf.d"

ssh -t $HOST -p $PORT "sudo apt install -y fail2ban"

ssh -t $HOST -p $PORT "sudo apt install -y ufw"
ssh -t $HOST -p $PORT "sudo ufw reset"
ssh -t $HOST -p $PORT "sudo ufw allow from 192.168.0.0/24 to any port $PORT"
ssh -t $HOST -p $PORT "sudo ufw allow from 192.168.1.0/24 to any port $PORT"
ssh -t $HOST -p $PORT "sudo ufw enable"
ssh -t $HOST -p $PORT "sudo ufw status verbose"
