.PHONY: help
help: ## Print this menu
	@grep -E '^[a-zA-Z_0-9-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

test: ## Run in test mode
	T=1 ./main.py # T=Test mode

upload: ## Upload script to Raspberry PI
	sshpass -e ssh -t pi@192.168.0.139 "mkdir -p ~/boot-selector"
	time sshpass -e scp *.py pi@192.168.0.139:/home/pi/boot-selector

fake-boot: ## Trigger script to start by emulating 
	echo "May 21 18:32:39 raspberrypi kernel: [ 8782.479267] dwc2 3f980000.usb: new device is full-speed" >> syslog
	echo "May 21 18:32:39 raspberrypi kernel: [ 8782.599108] dwc2 3f980000.usb: new device is high-speed" >> syslog
	echo "May 21 18:32:39 raspberrypi kernel: [ 8782.628944] dwc2 3f980000.usb: new address 1" >> syslog
	echo Gibberish ends >> syslog
