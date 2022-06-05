#!/usr/bin/env bash
mkdir -p ~/path

scp -r -P ${PORT} path $HOST:/home/pi

# https://stackoverflow.com/questions/3557037/appending-a-line-to-a-file-only-if-it-does-not-already-exist
LINE="export PATH=$PATH:~/path"
FILE="/home/pi/.bashrc"
grep -qF -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"

LINE="alias ll='ls -lrt'"
grep -qF -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"

