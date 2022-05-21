This program waits for a PC to boot, then initiates a key sequence to select Linux or Windows in the PC's
bios boot selector.

Reason: I am tired of doing it manually.

# Usage

* Connect to your Raspberry Pi Zero (tested with version 2) using some other guide
* 
* On the raspberry, run

```sh
python automate_boot_selection.py
```

# It doesn't work

* Setup depends on possibly very specific strings in `/var/log/syslog` which works for me. Replace
lines that look like `3f980000` in `automate_boot_selection.py` to whatever works for you.
* My PC uses F8 to launch boot device selector, change this if your PC use something else.
