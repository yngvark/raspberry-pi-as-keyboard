#!/usr/bin/env python3
import os
import time
import io

from user_error import UserError
from config import get_config

# Strategy: 

NULL_CHAR = chr(0)
config = get_config(os.getenv("D"))

KEYB_F8 = 65
KEYB_F12 = 69
KEYB_ARROW_DOWN = 81

if config["test_mode"] == True:
    print("Mode: TEST")
else:
    print("Mode: PRODUCTION")

def write_report(report):
    if config["test_mode"]:
        print(report.encode())
    else:
        do_write_report(report, 0)


def do_write_report(report, attemptCount):
    try:
        with open('/dev/hidg0', 'rb+') as fd:
            fd.write(report.encode())
    except FileNotFoundError as err:
        raise UserError(f"The raspberry pi is not connected to a USB port. Details: {err}")
    except BlockingIOError as err:
        if attemptCount == 20:
            print(f"Gave up after {attemptCount} attempts because of blocking io: {err}")
            return

        print(f"Waiting and retrying because of blocking io: {err}")
        time.sleep(0.5)
        do_write_report(report, attemptCount + 1)

def type(text):
    # See page 53 at https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf
    for char in text:
        if ord(char) == 32: # Space
            write_report(NULL_CHAR*2+chr(44)+NULL_CHAR*5)
            releaseKeys()
        else: # Normal letter
            usage_id = ord(char) - 93
            #print("USAGE ID: " + str(usage_id))

            write_report(NULL_CHAR*2+chr(usage_id)+NULL_CHAR*5)
            releaseKeys()


def releaseKeys():
    write_report(NULL_CHAR*8)


def typeEnter():
    write_report(NULL_CHAR*2+chr(40)+NULL_CHAR*5)
    releaseKeys()

    
def send_key_repeatedly(key, key_description):
    count = 10

    for i in range(0, count):
        print(f"Sending key: {key_description}")
        write_report(NULL_CHAR*2+chr(KEYB_F12)+NULL_CHAR*5)
        releaseKeys()
        time.sleep(1)


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
            line_3 = last_three_lines.pop()
            line_2 = last_three_lines.pop()
            line_1 = last_three_lines.pop()

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

def do_boot_sequence_with_keys(key, key_description):
    try:
        send_key_repeatedly(key, key_description)
    except UserError as err:
        print(f"Error: {err}")

def main():
    while True:
        print("Waiting for PC to boot...")
        wait_until_pc_boots()
        do_boot_sequence_with_keys(KEYB_F12, "F12")
        #do_boot_sequence_with_keys(KEYB_F8, "F8")

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



def prog1():
    type("echo hello world")
    typeEnter()

def prog3():
    write_report(NULL_CHAR*2+chr(KEYB_ARROW_DOWN)+NULL_CHAR*5)
    releaseKeys()



    
def test():
    # Press a
    write_report(NULL_CHAR*2+chr(4)+NULL_CHAR*5)
    # Release keys
    write_report(NULL_CHAR*8)
    # Press SHIFT + a = A
    write_report(chr(32)+NULL_CHAR+chr(4)+NULL_CHAR*5)

    # Press b
    write_report(NULL_CHAR*2+chr(5)+NULL_CHAR*5)
    # Release keys
    write_report(NULL_CHAR*8)
    # Press SHIFT + b = B
    write_report(chr(32)+NULL_CHAR+chr(5)+NULL_CHAR*5)

    # Press SPACE key
    write_report(NULL_CHAR*2+chr(44)+NULL_CHAR*5)

    # Press c key
    write_report(NULL_CHAR*2+chr(6)+NULL_CHAR*5)
    # Press d key
    write_report(NULL_CHAR*2+chr(7)+NULL_CHAR*5)

    # Press RETURN/ENTER key
    write_report(NULL_CHAR*2+chr(40)+NULL_CHAR*5)

    # Press e key
    write_report(NULL_CHAR*2+chr(8)+NULL_CHAR*5)
    # Press f key
    write_report(NULL_CHAR*2+chr(9)+NULL_CHAR*5)

    # Release all keys
    write_report(NULL_CHAR*8)

