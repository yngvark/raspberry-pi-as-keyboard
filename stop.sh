#!/usr/bin/env bash
function clearScreens() {
    # https://stackoverflow.com/a/14447172/915441
    SCREENS=$(screen -ls | tail +2 | grep boot | grep -o '[0-9]\{5\}')
    echo 

    for session in $(screen -ls | tail +2 | grep boot | grep -o '[0-9]\{5\}')
    do
        echo "Removing screen session: ${session}"
        screen -S "${session}" -X quit;
    done
}

touch stop_signal
clearScreens

#sudo screen -r boot -X stuff $'exit\n'
