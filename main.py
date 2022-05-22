#!/usr/bin/env python3
import os
import time
import io

from user_error import UserError
from config import get_config

# Strategy: 

NULL_CHAR = chr(0)
config = get_config(os.getenv("T"))

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


def wait_until_pc_boots():
    thefile = open(config["syslog_file"],"r")
    thefile.seek(0, io.SEEK_END)

    last_three_lines = []

    while True:
        line = thefile.readline()
        
        if not line:
            time.sleep(1)
            continue
        
        last_three_lines.append(line)

        if len(last_three_lines) == 3:
            line_3 = last_three_lines.pop().strip()
            line_2 = last_three_lines.pop().strip()
            line_1 = last_three_lines.pop().strip()

            print(line_1)
            print(line_2)
            print(line_3)

            if (
                "dwc2 3f980000.usb: new device is full-speed" in line_1
                and "dwc2 3f980000.usb: new device is high-speed" in line_2
                and "dwc2 3f980000.usb: new address 1" in line_3
                ):
                # PC has booted!
                break


    
def get_into_boot_device_menu_selection():
    count = 10

    for i in range(0, count):
        print(f"Sending key F8")
        send_bytes(NULL_CHAR*2+chr(KEYB_F8)+NULL_CHAR*5)
        releaseKeys()
        time.sleep(1)


def do_boot_sequence_with_keys():
    try:
        print("Sleeping 2 secs")
        time.sleep(2)

        get_into_boot_device_menu_selection()

        # Possible move selection down with arrow keys. Not now though.

        typeEnter()

    except UserError as err:
        print(f"Error: {err}")

def main():
    while True:
        print("Waiting for PC to boot...")
        wait_until_pc_boots()

        do_boot_sequence_with_keys()
        print("Boot sequence complete.")

        print("Waiting, hopefully the bios menu is in place in 5 seconds")
        time.sleep(5)

if __name__ == "__main__":
    main()

# When booting PC with raspberry inserted
#May 21 18:32:39 raspberrypi kernel: [ 8782.479267] dwc2 3f980000.usb: new device is full-speed
#May 21 18:32:39 raspberrypi kernel: [ 8782.599108] dwc2 3f980000.usb: new device is high-speed
#May 21 18:32:39 raspberrypi kernel: [ 8782.628944] dwc2 3f980000.usb: new address 1
#
#
# When putting raspberry into PC
#May 21 18:33:03 raspberrypi kernel: [ 8806.584807] dwc2 3f980000.usb: new device is high-speed
#May 21 18:33:04 raspberrypi kernel: [ 8806.718327] dwc2 3f980000.usb: new device is high-speed
#May 21 18:33:04 raspberrypi kernel: [ 8806.783694] dwc2 3f980000.usb: new address 1
