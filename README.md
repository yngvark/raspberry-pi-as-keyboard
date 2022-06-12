This program waits for a PC to boot, then initiates a key sequence to select Linux or Windows in the PC's
bios boot selector.

Reason: I am tired of doing it manually.

Inspiration and thanks to: https://randomnerdtutorials.com/raspberry-pi-zero-usb-keyboard-hid/

# Requirements

* You need to connect your Raspberry to your PC via an USB dongle like this:
https://www.digitalimpuls.no/pimoroni/149925/rpi-zero-usb-dongle-kit-usb-tilkobling-av-pi-zero
* You need to enable USB Gadget mode. Follow instructions in
https://randomnerdtutorials.com/raspberry-pi-zero-usb-keyboard-hid/

I also put it here in case it disappears:

```sh
pi@raspberrypi:~ $ echo "dtoverlay=dwc2" | sudo tee -a /boot/config.txt
pi@raspberrypi:~ $ echo "dwc2" | sudo tee -a /etc/modules
pi@raspberrypi:~ $ sudo echo "libcomposite" | sudo tee -a /etc/modules

pi@raspberrypi:~ $ sudo touch /usr/bin/isticktoit_usb
pi@raspberrypi:~ $ sudo chmod +x /usr/bin/isticktoit_usb

pi@raspberrypi:~ $ sudo nano /etc/rc.local

# Add the following before the line containing exit 0:
/usr/bin/isticktoit_usb # libcomposite configuration

pi@raspberrypi:~ $ sudo nano /usr/bin/isticktoit_usb
```

File contents:

```
#!/bin/bash
cd /sys/kernel/config/usb_gadget/
mkdir -p isticktoit
cd isticktoit
echo 0x1d6b > idVendor # Linux Foundation
echo 0x0104 > idProduct # Multifunction Composite Gadget
echo 0x0100 > bcdDevice # v1.0.0
echo 0x0200 > bcdUSB # USB2
mkdir -p strings/0x409
echo "fedcba9876543210" > strings/0x409/serialnumber
echo "Tobias Girstmair" > strings/0x409/manufacturer
echo "iSticktoit.net USB Device" > strings/0x409/product
mkdir -p configs/c.1/strings/0x409
echo "Config 1: ECM network" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower

# Add functions here
mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol
echo 1 > functions/hid.usb0/subclass
echo 8 > functions/hid.usb0/report_length
echo -ne \\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0 > functions/hid.usb0/report_desc
ln -s functions/hid.usb0 configs/c.1/
# End functions

ls /sys/class/udc > UDC
```

## Re-enable screen support - disable USB gadget mode

The above config somehow causes the screen to go black after reboot. Specifically, the dtooverlay=dwc2 is the
cause I think.

This following is supposed to make it possible to connect to the Raspberry from USB port only, but somehow it
fixes the screen issue, but disables USB gadget mode (which we need for our program to work.). So only use
this if you want to use the screen for debugging or whatnot. 

Or not, I am not actually sure anymore, somehow now both usb gadget mode works AND screen. Whatever, go debug
yourself. Anyway:

```bash
# This is the fix
sudo sed -i "s/rootwait/rootwait modules-load=dwc2/" /boot/cmdline.txt
touch /boot/ssh
sudo reboot
```

Source: https://www.digitalimpuls.no/pimoroni/149925/rpi-zero-usb-dongle-kit-usb-tilkobling-av-pi-zero

Pasting instructions here in case they disappear:

> Med dette kit'et kan du gjøre om en Raspberry Pi Zero til en USB dongle som du kan plugge rett inn i en PC for å få SSH tilgang, helt uten wifi eller ethernet adapter.
> 
> Noe konfigurasjon av Raspbian kreves:
> 
> 1. Åpne /boot/cmdline.txt for redigering
> 
> 2. Finn rootwait kommandoen og legg til modules-load=dwc2,g_ether etter rootwait
> 
> 3. Opprett en fil med navn ssh i bootmappa: /boot/ssh

To re-enable USB-gadget mode and disable screen, run:
```bash
# This is the fix
sudo sed -i "s/rootwait modules-load=dwc2/rootwait/" /boot/cmdline.txt
sudo reboot
```

### OLD STUFF - IGNORE


```bash
# This is the fix
sed "s/rootwait/rootwait modules-load=dwc2,g_ether/" /boot/cmdline.txt

touch /boot/ssh
```

# Setup the PI

From your own machine, run `pi-setup/setup.sh`

Run `pi-setup/setup.sh`

# Usage

* Connect to your Raspberry Pi Zero (tested with version 2) using some other guide
* Insert the Raspberry into your PC's USB port
* Edit makefile 
* On your machine, run

```shell
make pi-install-as-service
````

* Optional, if you have set up IFTTTT integration:


```shell
sudo nano /lib/systemd/system/boot-selector.service
````

Edit the following line

```
IFTTT_KEY=yourkey # replace yourkey with actual key
```

Save file.

* Reboot your PC. The python program should recognize this and start sending keystrokes to automate boot
selection.

# It doesn't work

* Setup depends on possibly very specific strings in `/var/log/syslog` which works for me. Replace
lines that look like `3f980000` in `main.py` to whatever works for you.
* My PC uses F8 to launch boot device selector, change this if your PC use something else.

# Developing

Developing workflow:

* Edit the Python files in this folder.
* Test them

```sh
make test
make fake-boot
````

* Set env var `SSHPASS` to the Raspberry's password.
* Run

```sh
make upload
````

* Re-boot PC with Raspberry connected to see if the program works as intented.

# ToDo

* Give access to correct user on boot: https://unix.stackexchange.com/questions/141255/give-a-specific-user-permissions-to-a-device-without-giving-access-to-other-user
* Create a physical switch to select OS: https://github.com/metachris/RPIO
