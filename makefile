f.PHONY: help
help: ## Print this menu
	@grep -E '^[a-zA-Z_0-9-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

run: ## Run
	sudo service boot-selector start
	sudo service status boot-selector

pi-run: ## Restart on Raspberry PI
	ssh -t pi@192.168.0.139 "cd /home/pi/boot-selector && make run"

restart: ## Restart locally
	sudo service restart boot-selector
	sudo service status boot-selector

pi-restart: ## Restart on Raspberry PI
	ssh -t pi@192.168.0.139 "cd /home/pi/boot-selector && make restart"

stop: ## Stop
	sudo ./stop.sh
	# echo Run: screen -r, and exit program. Then run exit.	

pi-stop: ## Restart on Raspberry PI
	ssh -t pi@192.168.0.139 "cd /home/pi/boot-selector && make stop"

pi-log: ## Show log from the Pi
	ssh -t pi@192.168.0.139 "tail -100 ~/boot-selector/log.txt"

# ------------------------------

test: ## Run in test mode
	touch syslog
	rm -f stop_signal
	T=1 ./main.py # T=Test mode

upload: ## Upload script to Raspberry PI
	ssh -t pi@192.168.0.139 "mkdir -p ~/boot-selector"
	scp makefile config.py main.py README.md user_error.py pi@192.168.0.139:/home/pi/boot-selector

fake-boot: ## Trigger script to start by emulating
	echo Gibberish starts >> syslog
	echo "May 21 18:32:39 raspberrypi kernel: [ 8782.479267] dwc2 3f980000.usb: new device is high-speed" >> syslog
	echo "May 21 18:32:39 raspberrypi kernel: [ 8782.599108] dwc2 3f980000.usb: new device is high-speed" >> syslog
	echo "May 21 18:32:39 raspberrypi kernel: [ 8782.628944] dwc2 3f980000.usb: new address 1" >> syslog
	echo Gibberish ends >> syslog

fake-boot-slow: ## Trigger script to start by emulating 
	echo Gibberish starts >> syslog
	sleep 1
	echo "May 21 18:32:39 raspberrypi kernel: [ 8782.479267] dwc2 3f980000.usb: new device is high-speed" >> syslog
	sleep 1
	echo "May 21 18:32:39 raspberrypi kernel: [ 8782.599108] dwc2 3f980000.usb: new device is high-speed" >> syslog
	sleep 1
	echo "May 21 18:32:39 raspberrypi kernel: [ 8782.628944] dwc2 3f980000.usb: new address 1" >> syslog
	sleep 1
	echo Gibberish ends >> syslog

pi-install-as-service: upload ## Run program when Raspberry boots.
	ssh -t pi@192.168.0.139 "mkdir -p /tmp/boot-selector-inst"
	scp boot-selector.service pi@192.168.0.139:/tmp/boot-selector-inst/boot-selector.service
	ssh -t pi@192.168.0.139 "sudo mv /tmp/boot-selector-inst/boot-selector.service /lib/systemd/system/boot-selector.service"
	ssh -t pi@192.168.0.139 "sudo systemctl daemon-reload"
	ssh -t pi@192.168.0.139 "sudo systemctl enable boot-selector"
	ssh -t pi@192.168.0.139 "sudo systemctl start boot-selector"
	ssh -t pi@192.168.0.139 "sudo systemctl status boot-selector"
