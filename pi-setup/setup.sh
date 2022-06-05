#!/usr/bin/env bash
# https://raspberrytips.com/security-tips-raspberry-pi/
HOST="pi@192.168.0.139"
PORT="1111"

# Add SSH Keys
if [[ ! -f authorized_keys ]]; then
    echo You need to create the file authorized_keys and insert public keys into it.
    exit 1
fi

ssh -t $HOST -p $PORT "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
scp -P $PORT authorized_keys $HOST:/home/pi/.ssh/authorized_keys
ssh -t $HOST -p $PORT "chmod 600 /home/pi/.ssh/authorized_keys"

# Secure PI settings
ssh -t $HOST -p $PORT "sudo cp /etc/ssh/sshd_config /tmp"
ssh -t $HOST -p $PORT "sudo sed -i 's/#Port 22/#Port 22\nPort 1111/' /etc/ssh/sshd_config"
ssh -t $HOST -p $PORT "sudo service ssh restart"

ssh -t $HOST -p $PORT "sudo apt install -y unattended-upgrades"
ssh -t $HOST -p $PORT "mkdir -p /tmp/secure-pi"

scp -P $PORT 02periodic $HOST:/tmp/secure-pi
ssh -t $HOST -p $PORT "sudo chown root:root /tmp/secure-pi/02periodic"
ssh -t $HOST -p $PORT "sudo mv /tmp/secure-pi/02periodic /etc/apt/apt.conf.d"

ssh -t $HOST -p $PORT "sudo apt install -y fail2ban"

ssh -t $HOST -p $PORT "sudo apt install -y ufw"
ssh -t $HOST -p $PORT "sudo ufw reset"
ssh -t $HOST -p $PORT "sudo ufw allow from 192.168.0.0/24 to any port $PORT"
ssh -t $HOST -p $PORT "sudo ufw allow from 192.168.1.0/24 to any port $PORT"
ssh -t $HOST -p $PORT "sudo ufw enable"
ssh -t $HOST -p $PORT "sudo ufw status verbose"

# Other setup
scp -P ${PORT} setup-path.sh $HOST:/tmp/setup-path.sh
ssh -t $HOST -p $PORT "/tmp/setup-path.sh"