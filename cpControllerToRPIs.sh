#!/bin/bash

# This will copy the mqttController.py to all RPIs.
# It will utilize scp.  It will prompt for the password

# Note: if replacing on a running system, you will need to restart the mqttcontroller service
#   sudo systemctl restart mqttcontroller.service


#scp ./mqttController.py pi@rpi-adblocker.local:./MySoftwareProjects/mqttController/
scp ./mqttController.py pi@rpi-misc.local:./MySoftwareProjects/mqttController/
scp ./getIP.sh pi@rpi-misc.local:./MySoftwareProjects/mqttController/
scp ./mqttController.py pi@rpi-printersvr.local:./MySoftwareProjects/mqttController/
scp ./getIP.sh pi@rpi-printersvr.local:./MySoftwareProjects/mqttController/
scp ./mqttController.py pi@rpi-dev.local:./MySoftwareProjects/mqttController/
scp ./getIP.sh pi@rpi-dev.local:./MySoftwareProjects/mqttController/
scp ./mqttController.py pi@rpi-media.local:./MySoftwareProjects/mqttController/
scp ./getIP.sh pi@rpi-media.local:./MySoftwareProjects/mqttController/


