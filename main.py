#!/usr/bin/env python3
import os
import time
import io
from os import path
import subprocess
from subprocess import Popen, PIPE
from datetime import datetime

from user_error import UserError
from config import get_config



# Strategy: 

NULL_CHAR = chr(0)
config = get_config(os.getenv("T"))

USER_ABORT = 1
PC_HAS_BOOTED = 2

KEYB_F8 = 65
KEYB_F12 = 69
KEYB_ARROW_DOWN = 81

COOLDOWN_TIME = 300

if config["test_mode"] == True:
    print("Mode: TEST")
else:
    print("Mode: PRODUCTION")

def log_print(text):
    # Get the current time
    now = datetime.now()

    # Format the timestamp without milliseconds
    formatted_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # Print the formatted timestamp
    print(formatted_timestamp + " " + text)


def send_bytes(bytez):
    if config["test_mode"]:
        print(bytez.encode())
    else:
        do_send_bytes(bytez, 0)


def do_send_bytes(bytez, attemptCount):
    try:
        with open('/dev/hidg0', 'rb+') as fd:
            fd.write(bytez.encode())
    except FileNotFoundError as err:
        raise UserError(f"The raspberry pi is not connected to a USB port. Details: {err}")
    except BlockingIOError as err:
        if attemptCount == 20:
            log_print(f"Gave up after {attemptCount} attempts because of blocking io: {err}")
            return

        log_print(f"Waiting and retrying because of blocking io: {err}")
        time.sleep(0.5)
        do_send_bytes(bytez, attemptCount + 1)

def type(text):
    # See page 53 at https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf
    for char in text:
        if ord(char) == 32: # Space
            send_bytes(NULL_CHAR*2+chr(44)+NULL_CHAR*5)
            releaseKeys()
        else: # Normal letter
            usage_id = ord(char) - 93
            #log_print("USAGE ID: " + str(usage_id))

            send_bytes(NULL_CHAR*2+chr(usage_id)+NULL_CHAR*5)
            releaseKeys()


def releaseKeys():
    send_bytes(NULL_CHAR*8)


def typeEnter():
    send_bytes(NULL_CHAR*2+chr(40)+NULL_CHAR*5)
    releaseKeys()


def get_epoch_time():
    return int(time.time())

def wait_until_pc_boots(last_boot_time_epoch):
    log_print("Reading from file: " + config["syslog_file"])

    thefile = open(config["syslog_file"],"r")
    thefile.seek(0, io.SEEK_END)

    log_print(f"File position: {thefile.tell()}")

    last_2_lines = []

    while True:
        if path.exists("stop_signal"):
            log_print("Found file stop_signal, exiting program")
            return USER_ABORT, 0

        line = thefile.readline()
        #log_print("readline:")
        #log_print(line)

        if not line: # There is no new line in syslog
            time.sleep(1)
            continue
        
        line = line.strip()

        if get_epoch_time() - last_boot_time_epoch < COOLDOWN_TIME:
            log_print("SYSLOG (ignoring): " + line)
            continue

        log_print("SYSLOG: " + line)
        last_2_lines.append(line)

        if len(last_2_lines) == 2:
            copy = last_2_lines[:]
            last_2_lines.pop(0)

            match1 = "dwc2 3f980000.usb: new device is high-speed" in copy[0]
            match2 = "dwc2 3f980000.usb: new address" in copy[1]

            #log_print("Checking last two lines:")
            #log_print(f"    {copy[0]} - {match1}")
            #log_print(f"    {copy[1]} - {match2}")

            if (match1 and match2):
                # PC has booted!
                nowtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_print(f"PC has booted at {nowtime}")
                return PC_HAS_BOOTED, get_epoch_time()


def run_cmd(cmd):
    log_print("Running cmd: " + ' '.join(cmd))
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    output, error = p.communicate()
    if p.returncode != 0: 
        print("ERROR, response from cmd (exit code %d): %s %s" % (p.returncode, output, error), file=sys.stderr)

    print(output)


def send_alert():
    ifttt_key = os.getenv("IFTTT_KEY")
    if ifttt_key:
        url = f"https://maker.ifttt.com/trigger/reminder/with/key/{ifttt_key}?value1=X&value2=F8started"
        cmd = ["curl", "--silent", "-X", "POST", url]
        run_cmd(cmd)
    else:
        log_print("IFTTT_KEY not present, not sending alert")


def get_into_boot_device_menu_selection():
    send_alert()

    count = 5

    for i in range(0, count):
        log_print(f"Sending key F8")
        send_bytes(NULL_CHAR*2+chr(KEYB_F8)+NULL_CHAR*5)
        releaseKeys()
        time.sleep(1)


def do_boot_sequence_with_keys():
    try:
        #log_print("Sleeping 2 secs")
        #time.sleep(2)

        get_into_boot_device_menu_selection()

        # Possible move selection down with arrow keys. Not now though.

        typeEnter()

    except UserError as err:
        log_print(f"Error: {err}")

def main():
    last_epoc_time = 0

    while True:
        nowtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        log_print("")
        log_print(f"Waiting for PC to boot... Time is {nowtime}")
        result, last_epoc_time = wait_until_pc_boots(last_epoc_time)
        if result == USER_ABORT:
            log_print("Exiting program")
            break

        do_boot_sequence_with_keys()
        log_print("Boot sequence complete.")

        log_print("Waiting, hopefully the bios menu is in place in 5 seconds")
        time.sleep(5)

if __name__ == "__main__":
    main()
