#!/usr/bin/env bash
# sudo useradd --create-home booter
# sudo passwd booter

# sudo udevadm info -a /dev/hidg0
# sudo nano /etc/udev/rules.d/99-usb-keyboard-writer.rules
# SUBSYSTEM=="block", ATTRS{idProduct}=="Multifunction Composite Gadget", ACTION=="add", RUN+="/bin/chmod 777 /dev/$name"
# SUBSYSTEM=="block", KERNEL=="hidg0", SUBSYSTEM=="hidg", ACTION=="add", RUN+="/bin/chmod 777 /dev/$name"

# ACTION=="remove", ENV{ID_VENDOR_ID}=="1050", ENV{ID_MODEL_ID}=="0407", RUN+="/usr/local/bin/lockscreen"
# SUBSYSTEM=="block", ATTRS{idProduct}=="0727", ATTRS{serial}=="000000000207", ACTION=="add", RUN+="/bin/chmod 777 /dev/$name"

# SUBSYSTEM=="block", ATTRS{idProduct}=="0727", ATTRS{serial}=="000000000207", ACTION=="add", RUN+="/bin/setfacl -m u:patrick:rw- /dev/$name"


#sudo ls -lrt /dev/hidg0
