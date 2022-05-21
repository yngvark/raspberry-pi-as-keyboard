#!/usr/bin/env python3
import os

# Strategy: 


NULL_CHAR = chr(0)
DRY_RUN = os.getenv("SENDKEYS_DRYRUN")

KEYB_F12 = 69

if DRY_RUN:
    print("Mode: DRY RUN")

def write_report(report):
    if DRY_RUN:
        print(report.encode())
    else:
        with open('/dev/hidg0', 'rb+') as fd:
            fd.write(report.encode())

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


def prog1():
    type("echo hello world")
    typeEnter()

def prog2():
    for i in range(0,2):
        write_report(NULL_CHAR*2+chr(KEYB_F12)+NULL_CHAR*5)
        releaseKeys()

prog2()
