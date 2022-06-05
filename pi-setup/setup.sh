#!/usr/bin/env bash
# All changes in this file should be idempotent.

PORT=""
if [[ -z "$1" ]]; then
    echo Missing arg 1: port
    exit 1
else
    PORT=$1
fi

if [[ -z "$1" ]]; then
    echo Missing env var: USER_PW
    exit 1
fi

echo Settings:
echo pwd: $(pwd)
echo Port: $PORT

# Authorized keys
echo
echo "Setting authorized keys"
mkdir -p ~/.ssh && chmod 700 ~/.ssh
cp authorized_keys /home/pi/.ssh/authorized_keys
chmod 600 /home/pi/.ssh/authorized_keys

# Secure PI settings
# https://raspberrytips.com/security-tips-raspberry-pi/

# Change SSH port
echo
echo "Changing SSH port"
sudo cp /etc/ssh/sshd_config /tmp/sshd_config.bak

# https://stackoverflow.com/questions/3557037/appending-a-line-to-a-file-only-if-it-does-not-already-exist
FILE="/etc/ssh/sshd_config"
if ! grep -Fxq "Port $PORT" "$FILE"; then
    sudo sed -i 's/#Port 22/#Port 22\nPort 1111/' /etc/ssh/sshd_config
    echo sudo service ssh restart
fi

# Install unattended-upgrades
echo
echo "Install unattended-upgrades"
sudo apt install -y unattended-upgrades

sudo chown root:root /tmp/secure-pi/02periodic
sudo mv /tmp/secure-pi/02periodic /etc/apt/apt.conf.d

# Fail2ban
echo
echo "Install fail2ban"
sudo apt install -y fail2ban

# UFW firewall
echo
echo "Install UFW firewall"
sudo apt install -y ufw
sudo ufw reset
sudo ufw allow from 192.168.0.0/24 to any port $PORT
sudo ufw allow from 192.168.1.0/24 to any port $PORT
sudo ufw enable
sudo ufw status verbose

# Other setup
echo
echo "Setup PATH"
rm -rf /home/pi/path || true
mv path /home/pi
./setup-path.sh
