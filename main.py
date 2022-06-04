#!/usr/bin/env python3
import os
import time
import io
from os import path

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

if config["test_mode"] == True:
    print("Mode: TEST")
else:
    print("Mode: PRODUCTION")

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
            print(f"Gave up after {attemptCount} attempts because of blocking io: {err}")
            return

        print(f"Waiting and retrying because of blocking io: {err}")
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
            #print("USAGE ID: " + str(usage_id))

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
    print("Reading from file: " + config["syslog_file"])

    thefile = open(config["syslog_file"],"r")
    thefile.seek(0, io.SEEK_END)

    last_2_lines = []

    while True:
        line = thefile.readline()
        #print("readline:")
        #print(line)

        if not line:
            if path.exists("stop_signal"):
                print("Found file stop_signal, exiting program")
                return USER_ABORT, 0

            time.sleep(1)
            continue
        
        line = line.strip()

        # Probably 60 is better, but just to be sure eh
        if get_epoch_time() - last_boot_time_epoch < 90:
            print("SYSLOG (ignoring): " + line)
            continue

        print("SYSLOG: " + line)
        last_2_lines.append(line)

        if len(last_2_lines) == 2:
            copy = last_2_lines[:]
            last_2_lines.pop(0)

            print("Checking last two lines")

            if (
                    "dwc2 3f980000.usb: new device is high-speed" in copy[0]
                and "dwc2 3f980000.usb: new address 1" in copy[1]
                ):
                # PC has booted!
                print("PC has booted!")
                return PC_HAS_BOOTED, get_epoch_time()


#        if len(last_2_or_3_lines) == 2:
#            copy = last_2_or_3_lines[:]
#            print("Checking last two lines")
#
#            if (
#                    "dwc2 3f980000.usb: new device is high-speed" in copy[0]
#                and "dwc2 3f980000.usb: new address 1" in copy[1]
#                ):
#                # PC has booted!
#                print("PC has booted!")
#                return PC_HAS_BOOTED, get_epoch_time()
#
#        if len(last_2_or_3_lines) == 3:
#            copy = last_2_or_3_lines[:]
#            last_2_or_3_lines.pop(0)
#            print("Checking last three lines")
#
#            if (
#                   ("dwc2 3f980000.usb: new device is high-speed" in copy[0] or "dwc2 3f980000.usb: new device is full-speed" in copy[0])
#                and "dwc2 3f980000.usb: new device is high-speed" in copy[1]
#                and "dwc2 3f980000.usb: new address 1" in copy[2]
#                ):
#                # PC has booted!
#                print("PC has booted!")
#                return PC_HAS_BOOTED, get_epoch_time()

def get_into_boot_device_menu_selection():
    count = 5

    for i in range(0, count):
        print(f"Sending key F8")
        send_bytes(NULL_CHAR*2+chr(KEYB_F8)+NULL_CHAR*5)
        releaseKeys()
        time.sleep(1)


def do_boot_sequence_with_keys():
    try:
        #print("Sleeping 2 secs")
        #time.sleep(2)

        get_into_boot_device_menu_selection()

        # Possible move selection down with arrow keys. Not now though.

        typeEnter()

    except UserError as err:
        print(f"Error: {err}")

def main():
    last_epoc_time = 0

    while True:
        print("")
        print("Waiting for PC to boot...")
        result, last_epoc_time = wait_until_pc_boots(last_epoc_time)
        if result == USER_ABORT:
            print("Exiting program")
            break

        do_boot_sequence_with_keys()
        print("Boot sequence complete.")

        print("Waiting, hopefully the bios menu is in place in 5 seconds")
        time.sleep(5)

if __name__ == "__main__":
    main()
