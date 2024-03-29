HOST := "pi@192.168.0.139"
PORT := "1111"

.PHONY: help
help: ## Print this menu
	@grep -E '^[a-zA-Z_0-9-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

run: ## Run
	sudo systemctl start boot-selector
	sudo systemctl status boot-selector

pi-run: ## Restart on Raspberry PI
	ssh -t ${HOST} -p ${PORT} "cd /home/pi/boot-selector && make run"

restart: ## Restart locally
	sudo systemctl restart boot-selector
	sudo systemctl status boot-selector

pi-restart: ## Restart on Raspberry PI
	ssh -t ${HOST} -p ${PORT} "cd /home/pi/boot-selector && make restart"

stop: ## Stop
	sudo systemctl stop boot-selector

pi-stop: ## Restart on Raspberry PI
	ssh -t ${HOST} -p ${PORT} "cd /home/pi/boot-selector && make stop"

status:
	sudo systemctl status boot-selector

pi-status:
	ssh -t ${HOST} -p ${PORT} "cd /home/pi/boot-selector && make status"

pi-log: ## Show log from the Pi
	ssh -t ${HOST} -p ${PORT} "sudo cp /home/pi/boot-selector/log.txt /tmp/log.txt && sudo chown pi:pi /tmp/log.txt"
	scp -P ${PORT} ${HOST}:/tmp/log.txt /tmp/pi-log.txt
	less /tmp/pi-log.txt
	rm /tmp/pi-log.txt

pi-syslog: ## Show syslog from the Pi
	scp -C -P ${PORT} ${HOST}:/var/log/syslog /tmp/pi-syslog.txt
	less /tmp/pi-syslog.txt
	rm /tmp/pi-syslog.txt

pi-err: ## Show error log from the Pi
	ssh -t ${HOST} -p ${PORT} "sudo cp /home/pi/boot-selector/log-err.txt /tmp/log-err.txt && sudo chown pi:pi /tmp/log-err.txt"
	scp -P ${PORT} ${HOST}:/tmp/log-err.txt /tmp/pi-err.txt
	less /tmp/pi-err.txt
	rm /tmp/pi-err.txt

download-logs: ## Download all logs to /tmp
	ssh -t ${HOST} -p ${PORT} "sudo cp /home/pi/boot-selector/log.txt /tmp/log.txt && sudo chown pi:pi /tmp/log.txt"
	scp -P ${PORT} ${HOST}:/tmp/log.txt /tmp/pi-log.txt

	scp -C -P ${PORT} ${HOST}:/var/log/syslog /tmp/pi-syslog.txt

	ssh -t ${HOST} -p ${PORT} "sudo cp /home/pi/boot-selector/log-err.txt /tmp/log-err.txt && sudo chown pi:pi /tmp/log-err.txt"
	scp -P ${PORT} ${HOST}:/tmp/log-err.txt /tmp/pi-err.txt

tail:
	tail -f log.txt

pi-tail: ## Tail log from the Pi
	ssh -t ${HOST} -p ${PORT} "cd /home/pi/boot-selector && make tail"

pi-ls: ##
	ssh -t ${HOST} -p ${PORT} "ls -lrtaH /home/pi/boot-selector --color"

gui: ## Show log in Pi GUI. Has to be run from the Pi, because it otherwise hangs.
	echo "This currently doesn't work, because log.txt is owned by root."
	sudo ./open-log-gui.sh log.txt &

pi-gui: ## Start a terminal tailing the log
	ssh -t ${HOST} -p ${PORT} "cd ~/boot-selector && make gui"

ssh: ## ssh into the Pi
	ssh ${HOST} -p ${PORT}

logrotate: ## Force a log rotation
	sudo logrotate -f /etc/logrotate.d/boot-selector

# ------------------------------ DEVELOPING

test: ## Run in test mode
	touch syslog
	rm -f stop_signal
	T=1 ./main.py # T=Test mode

pi-test:
	ssh -t ${HOST} -p ${PORT} "logger '[ 8782.479267] dwc2 3f980000.usb: new device is high-speed' && logger '[ 8782.479267] dwc2 3f980000.usb: new address 5'"

upload: ## Upload script to Raspberry PI
	ssh -t ${HOST} -p ${PORT} "mkdir -p ~/boot-selector"
	scp -P ${PORT} makefile config.py main.py README.md user_error.py test_write.py open-log-gui.sh ${HOST}:/home/pi/boot-selector
	@make pi-restart

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

# ------------------------------ INSTALLATION

pi-install: upload ## Run program when Raspberry boots.
	@make pi-install-service
	@make pi-install-logrotate

pi-install-service: ##
	ssh -t ${HOST} -p ${PORT} "mkdir -p /tmp/boot-selector-inst"
	scp -P ${PORT} boot-selector.service ${HOST}:/tmp/boot-selector-inst/boot-selector.service
	ssh -t ${HOST} -p ${PORT} "sudo mv /tmp/boot-selector-inst/boot-selector.service /lib/systemd/system/boot-selector.service"
	ssh -t ${HOST} -p ${PORT} "sudo systemctl daemon-reload"
	ssh -t ${HOST} -p ${PORT} "sudo systemctl enable boot-selector"
	ssh -t ${HOST} -p ${PORT} "sudo systemctl start boot-selector"
	ssh -t ${HOST} -p ${PORT} "sudo systemctl status boot-selector"

pi-install-logrotate: ##
	scp -P ${PORT} boot-selector.logrotate ${HOST}:/tmp/boot-selector-inst/boot-selector.logrotate
	ssh -t ${HOST} -p ${PORT} "sudo mv /tmp/boot-selector-inst/boot-selector.logrotate /etc/logrotate.d/boot-selector"
	ssh -t ${HOST} -p ${PORT} "sudo chown root:root /etc/logrotate.d/boot-selector"
	ssh -t ${HOST} -p ${PORT} "sudo chmod 644 /etc/logrotate.d/boot-selector"
