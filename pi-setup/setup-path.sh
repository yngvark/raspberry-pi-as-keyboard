#!/usr/bin/env bash
# https://stackoverflow.com/questions/3557037/appending-a-line-to-a-file-only-if-it-does-not-already-exist
FILE="/home/pi/.bashrc"

LINE="export PATH=$PATH:/home/pi/path"
grep -qF -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"

LINE="alias ll='ls -lrt'"
grep -qF -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"
