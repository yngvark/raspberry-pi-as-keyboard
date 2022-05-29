#!/usr/bin/env bash
rm -f stop_signal

GREP_STRING="sudo python main.py"
RUNNING=$(ps aux | grep "$GREP_STRING" | grep -v grep | wc -l)

if [[ ! $RUNNING -eq 0 ]]; then
    echo App is running, not doing anything.
    exit 0
fi

# Problem: This creates more instances, so in stop.sh we have to stop after every run.
sudo screen -S boot -d -m -L

sudo screen -r boot -X stuff $'sudo python main.py\n'
