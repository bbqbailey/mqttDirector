#!/usr/bin/python3
import paho.mqtt.client as mqtt
import os
import subprocess
MQTT_DIRECTOR_VERSION = "mqttDirector.py Version: 1.0 Date Dec 22, 2018"
MQTT_SERVER = "192.168.1.208"  # Hottub mqtt server/broker
MQTT_TOPIC_SUBSCRIBE = "CONTROLLER/ACTION"
MQTT_TOPIC_PUBLISH = "CONTROLLER/RESPONSE"
NODENAME = os.uname().nodename  
LOG_FILE = "mqttActions.txt"  #  a logging file


def DEBUG(msg):
    if  __debug__: 
        print(msg)

actionDict = {}


# log actions
def logActions(action):
    os.system("echo -n \"" + action + ": \" >> mqttActions.txt")
    os.system("date >> mqttActions.txt")


#display menu
def _menu():
    DEBUG("\nmenu() entry")
    print()
    print()
    print()
    print("====== mqttDirector ======")
    print()
    print()
    print("Utility to control systems subscribed to MQTT topic CONTROLLER/ACTION")
    print()
    print("mqttDirector Action Menu")
    print("------------------------")
    print("<Form is 'Command Description'.  E.g., issue 'shutdown' to shutdown all systems.>")
    print()
    print()
    print("\tshutdown        Shutdown all systems.")
    print("\treboot          Reboot all systems.")
    print("\techo            Echo will cause all systems to reply with their hostname")
    print("\tblink <RPI>     Blink specified RPI (e.g., blink RPI-DEV) to blink for 1 minute.")
    print("\tnewLog          NewLog will create new logging file, and increment existing to version +1")
    print("\tversion         Version of mqttDirector.py (this application): ")
    print("\tosRelease       request the OS version info from each RPI")
    print("\thelp            Help displays commands that can be invoked")
    print()
    print("\texit         Exit this programe only; subscribers still monitoring MQTT Topic CONTROLLER/ACTION")
    print()
    command = str.upper(input("Please enter your command: "))
    print(">>>  Command received: " + command)
    print()

    _action(command)
    _menu()


# determine the appropriate control action contained in mqtt message
def _action(strReceived):
    DEBUG("\n_action() entry, strReceived: " + strReceived)

    actionDict = {
        "SHUTDOWN": shutdown,
        "REBOOT": reboot,
        "ECHO": echo,
        "BLINK": _blink_on,
        "NEWLOG": newLog,
        "VERSION": version,
        "OS": osRelease,
        "NODENAME": _nodename,
        "HELP": help,
        "EXIT": exit
    }

    if strReceived not in actionDict:
        _unknownAction(strReceived)
    else:
        callFunction = actionDict[strReceived]

    callFunction()
            
    DEBUG("_action() exit\n")

# sends command via MQTT to Topic:Command
def _sendCommand(command):
    DEBUG("\n_sendCommand() entry")
    print("Sending command: " + command)
    date = subprocess.check_output('date').decode('ascii')
    response = 'mosquitto_pub -h ' + MQTT_SERVER + ' -t ' + '\"' + MQTT_TOPIC_SUBSCRIBE + '\" -m \"App: mqttDirector; Nodename: ' + NODENAME + ' Message: ' + command + ' ' + date  + '\"' 
    os.system(response)
    _response(command)
    DEBUG("\n_sendCommand() exit")


# shutdown():
def shutdown():
    msg = ">>>> shutdown <<<<"
    DEBUG("\nshutdown() entry")
    logActions("Shutdown")
    print(msg)
    _sendCommand("SHUTDOWN")
    _response(msg)
    DEBUG("shutdown() exit\n")


# reboot the system
def reboot():
    msg = ">>>> rebooting <<<<"
    DEBUG("\nreboot() entry")
    logActions("Reboot")
    print(">>>rebooting<<<")
    _sendCommand("REBOOT")
    _response(msg)
    DEBUG("reboot() exit\n")


# echoo a message, specific to this instance,  back to the controller
def echo():
    msg = " >>> Online and Functioning. <<<<"

    DEBUG("\necho() entry")
    logActions("echoing this node name back to mqtt server")
    _sendCommand("ECHO")
    _response(msg)
    DEBUG("echo() exit")


# blink onboard led
def _blink_on(strReceived):
    msg = " >>> BLINKING LED <<<<"

    DEBUG("\n_blink_on() entry")
    logActions("Blinking LED on specified Node")
    _sendCommand(strReceived)
    _response(msg)
    DEBUG("echo() exit")


# refresh the log.  Keep 5 version
def newLog():
    msg = " >>>> Creating New Log, and bumping old versions +1 <<<<"
    DEBUG("\nnewLog() entry")
    _sendCommand("NEWLOG")
    _response(msg)
    print("Created new logging file and incrementing old versions to +1.")
    DEBUG("newLog() exit")


# version - respond with the version of this code mqttDirector.py
def version():
    DEBUG("\nversion() entry")
    logActions("Responding with version of mqttDirectorpy")
    _sendCommand("VERSION")
    _response(MQTT_DIRECTOR_VERSION)
    DEBUG("version() exit")


# version - respond with the version of this code mqttDirector.py
def osRelease():
    msg = " >>> OSRELEASE Version Info <<<<"
    DEBUG("\nosRelease() entry")
    logActions("Responding with /etc/os-release info.")
    _sendCommand("OSRELEASE")
    _response(msg)
    DEBUG("osRelease() exit")


# help - list the known commands and etc
def help():
    msg = ">>>> help <<<<"
    DEBUG("\nhelp() entry")
    logActions("Replying to 'help' request")
    print("\nCommands recognized for MQTT topic " + MQTT_TOPIC_SUBSCRIBE + ":")
    print("\tshutdown     - shuts all participating systems down.")
    print("\treboot       - reboots all participating systems.")
    print("\techo         - send an echo response to topic: " + MQTT_TOPIC_PUBLISH)
    print("\tblink <node> - send a request to the specific <node> to perform a blink to help locate it.")
    print("\tnewLog       - increments all logs; creates and uses new log")
    print("\tversion      - cause RPIs to provide their version number of mqttController.py")
    print("\tosRelease    - cause RPIs to run /etc/os-release, showing OS version info, etc")
    print("\thelp         - lists the commands, etc.")
    print()

    _response(msg)
    DEBUG("\nhelp() exit")


# deal with unknown command actions received def unknownAction(msg):
def _unknownAction(strReceived):
    msg = ">>>> Unknown Action Requested <<<<"
    DEBUG("\n_unknownAction() entry")
    logActions("Ignoring Unknown Action: " + strReceived)
    print(">>>Ignoring Unknown Action<<<")
    _response("  >>> " + strReceived + " is an Unknown Command and is Ignored. <<<<")
    DEBUG("_unknownAction() exit\n")


# send response to commands
def _response(msg):
    DEBUG("\nresponse() entry")
    logActions("Responding with msg: " + msg)
    date = subprocess.check_output('date').decode('ascii')
    response = 'mosquitto_pub -h ' + MQTT_SERVER + ' -t ' + '\"' + MQTT_TOPIC_PUBLISH + '\" -m \"App: mqttDirectory.py, Nodename: ' + NODENAME + ' Message: ' + msg + ' ' + date + '\"'
    os.system(response)
    DEBUG("\nresponse() exit")


# ignore any received NODENAME message
def _nodename(strReceived):
    DEBUG("\nnodename() entry")
    logActions("Ignoring  NODENAME Action as it is just an echo of an echo!")
    print(">>>Ignoring NODENAME Action<<<")
    DEBUG("nodename() exit\n")


# ================code to connect and receive mqtt messages===============

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    DEBUG("\non_connect() entry")
    print(" Connected with result code "+str(rc))
    logActions("\n>>>Connected with result code<<<" + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC_SUBSCRIBE)
    DEBUG("on_connect() exit\n")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    DEBUG("\non_message() entry\n")
    strReceived = msg.payload.decode('ascii').upper()
    logActions(msg.topic + " : " + strReceived)
    DEBUG("on_message() topic : message >>> " + msg.topic + " : " + strReceived)
    _action(strReceived)
    DEBUG("on_message() exit\n")

_response("Starting.... " + MQTT_DIRECTOR_VERSION)
_menu()
print("should not be here")
exit()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
