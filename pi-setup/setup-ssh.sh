#!/usr/bin/env bash
# https://raspberrytips.com/security-tips-raspberry-pi/
HOST="pi@192.168.0.139"
PORT="1111"
TMP_DIR="/tmp/pi-setup"

# Add SSH Keys
if [[ ! -f authorized_keys ]]; then
    echo You need to create the file authorized_keys and insert public keys into it.
    exit 1
fi

ssh -t $HOST -p $PORT "mkdir -p /tmp/pi-setup"

FILES="authorized_keys 02periodic setup-path.sh setup.sh path"
echo Copying files...
scp -r -P $PORT $FILES $HOST:$TMP_DIR
echo
echo Running setup...
echo ssh -t $HOST -p $PORT "cd $TMP_DIR && ./setup.sh $PORT"
ssh -t $HOST -p $PORT "cd $TMP_DIR && ./setup.sh $PORT"
