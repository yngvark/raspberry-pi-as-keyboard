.PHONY: help
help: ## Print this menu
	@grep -E '^[a-zA-Z_0-9-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

upload:
	time sshpass -f /tmp/pw.txt scp sendkeys.py pi@192.168.0.139:/home/pi
	#time sshpass -f /tmp/pw.txt scp *.py pi@192.168.0.139:/home/pi

fake-boot:
	echo May 21 18:32:39 raspberrypi kernel: [ 8782.479267] dwc2 3f980000.usb: new device is full-speed >> syslog
	echo May 21 18:32:39 raspberrypi kernel: [ 8782.599108] dwc2 3f980000.usb: new device is high-speed >> syslog
	echo May 21 18:32:39 raspberrypi kernel: [ 8782.628944] dwc2 3f980000.usb: new address 1 >> syslog
	echo Gibberish ends >> syslog
