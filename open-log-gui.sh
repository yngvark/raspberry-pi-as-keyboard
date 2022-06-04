#!/bin/sh
# This crazy script is needed to lock screen when running this script as root. See OS setup scripts
# lockscreen.sh for how it is called (per now: /etc/udev/rules.d/85-yubikey.rules).

# Based on https://raw.githubusercontent.com/aminb/usb-lock/master/onusbunplug.sh

ENABLED=true

getXuser() {
        user=`pinky| grep -m1 ":$displaynum" | awk '{print $1}'`
 
        if [ x"$user" != x"" ]; then
                userhome=`getent passwd $user | cut -d: -f6`
                export XAUTHORITY="$userhome/.Xauthority"
        else
                export XAUTHORITY=""
        fi
}

if [ ! $ENABLED = "true" ]; then
    exit 0
fi

for x in /tmp/.X11-unix/*; do
    displaynum=`echo $x | sed s#/tmp/.X11-unix/X##`
    getXuser
    if [ x"$XAUTHORITY" != x"" ]; then
        # extract current state
        export DISPLAY=":$displaynum"
    fi
done

su "$user" -c "lxterminal -e tail -f $1"

