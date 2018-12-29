#!/usr/bin/python3
import paho.mqtt.client as mqtt
import os
import subprocess
import time


#MQTT_CONTROLLER_VERSION = "mqttController.py Version: 1.0 Date Dec 22, 2018"
MQTT_CONTROLLER_VERSION = "mqttController.py Version: 1.1 Date Dec 29, 2018"
MQTT_SERVER = "192.168.1.208"  # mqtt server/broker
MQTT_TOPIC_SUBSCRIBE = "CONTROLLER/ACTION"
MQTT_TOPIC_PUBLISH = "CONTROLLER/RESPONSE"
USER_HOME = os.environ['HOME']
print("user home: " + USER_HOME)
NODENAME = os.uname().nodename
LOG_FILE = USER_HOME + "/MySoftwareProjects/mqttController/mqttActions.txt"


def DEBUG(msg):
    if __debug__: 
        print(msg)


def logActions(action):
    """ Log 'action' to logging file """
    os.system("echo -n \"" + action + ": \" >> " + LOG_FILE)
    os.system("date >> " + LOG_FILE)


def _action(strReceived):
    """ determine the appropriate control action contained in mqtt message"""

    DEBUG("\n_action() entry, strReceived: " + strReceived)
    if (strReceived.find('REBOOT') != -1):
        reboot()
    elif (strReceived.find('SHUTDOWN') != -1):
        shutdown()
    elif (strReceived.find('ECHO') != -1):
        echo()
    elif (strReceived.find('BLINK') != -1):
        _blink_on(strReceived)
    elif (strReceived.find('NEWLOG') != -1):
        newLog()
    elif (strReceived.find('VERSION') != -1):
        version()
    elif (strReceived.find('OSRELEASE') != -1):
        osRelease()
    elif (strReceived.find('DF') != -1):
        df()
    else:
        _unknownAction(strReceived)
    DEBUG("_action() exit\n")


def shutdown():
    """Send a SHUTDOWN command to all subscbers"""
    msg = ">>>> shutdown <<<<"
    DEBUG("\nshutdown() entry")
    logActions("Shutdown")
    print(msg)
    _response(msg)
    DEBUG("shutdown() exit\n")

    os.system("sudo shutdown")


def reboot():
    """Send a REBOOT command to all subscribers"""
    msg = ">>>> rebooting <<<<"
    DEBUG("\nreboot() entry")
    logActions("Reboot")
    print(">>>rebooting<<<")
    _response(msg)
    DEBUG("reboot() exit\n")

    os.system("sudo reboot")


def echo():
    """echoo a message, specific to this instance,  back to the controller"""

    msg = " >>> Online and Functioning. <<<<"

    DEBUG("\necho() entry")
    logActions("echoing this node name back to mqtt server")
    _response(msg)
    DEBUG("echo() exit")


def _blink_on(strReceived):
    """Blinking On - sometimes I'm not sure which RPI I need to disconnect.
       - sending a blinking_on command to just this RPI will provide capability
       - blink 60 times.
       - Before returning, will set the led mode to cpu0
       """
    strReceived = strReceived.upper()
    nodename = NODENAME.upper()
    DEBUG("\n_blinking_on() entry, strReceived: " + strReceived)

    # determine if I'm the RPI that needs to blink
    if (strReceived.find(nodename) != -1):
        DEBUG("_blinking_on(): activated for me! ")
        logActions("Blinking " + nodename)
        _response("Blinking " + nodename)

        for x in range(1, 60):
            # turn led on for 1/4 sec
            os.system("echo 1 | sudo tee /sys/class/leds/led1/brightness 1>/dev/null")
            time.sleep(0.25)  # pause (sleep) for 1/4 second
            #  turn led off for 1/4 sec
            os.system("echo 0 | sudo tee /sys/class/leds/led1/brightness 1>/dev/null")
            time.sleep(0.25)
        #  return to normal operation
        os.system("echo cpu0 | sudo tee /sys/class/leds/led1/trigger")
    else:
        DEBUG("\n_blinking_on(): was not requesting me: " + nodename)

    DEBUG("_blinking_on() exit\n")


#  refresh the log.  Keep 5 version
def newLog():
    msg = " >>>> Creating New Log, and bumping old versions +1 <<<<"
    DEBUG("\nnewLog() entry")
   
    os.system("mv " + LOG_FILE + "4 " + LOG_FILE + "5")
    os.system("mv " + LOG_FILE + "3 " + LOG_FILE + "4")
    os.system("mv " + LOG_FILE + "2 " + LOG_FILE + "3")
    os.system("mv " + LOG_FILE + " " + LOG_FILE + "2 2>> " + LOG_FILE)
    os.system("echo -n \"New log started: \" > " + LOG_FILE)
    os.system("date >> " + LOG_FILE)


    _response(msg)
    print("Created new logging file and incrementing old versions to +1.")
    DEBUG("newLog() exit")


# osRelease obtain the output from /etc/os-release for os information
def osRelease():
    msg = " >>>> Requesting OS Release information via cat /etc/os-release <<<< "
    DEBUG("\nosRelease() entry")
    strReceived = subprocess.check_output(['cat', '/etc/os-release']).decode('ascii')
    osList = []
    osList = strReceived.split("\n")

    version = osList[1]
    version = version.replace("(", "")
    version = version.replace(")", "")
    version = version.replace('"', '')

    print("OS Version: " + version)

    logActions("OS Version: " + version)
    _response("OS Version: " + version)


# echoo a message, specific to this instance,  back to the controller
def version():
    msg = " >>> VERSION " + MQTT_CONTROLLER_VERSION + "  <<<< "

    print("msg: " + msg)
    DEBUG("\nversion() entry")
    logActions("Version: " + msg)
    _response(msg)
    DEBUG("version() exit")

# df - file system disk space usage
def df():
    msg = " >>>> DF <<<< "

    DEBUG("\ndf() entry")
    print("msg: " + msg)
    strReceived = subprocess.check_output(['df', '-lh']).decode('ascii')
    print("return after df call")
    print("df: " + strReceived)
    logActions("df " + strReceived)
    _response("df: " + strReceived)
    DEBUG("\ndf() exit")



# deal with unknown command actions received def unknownAction(msg):
def _unknownAction(strReceived):
    msg = ">>>> Unknown Action Requested <<<<"
    DEBUG("\n_unknownAction() entry")
    logActions("Ignoring Unknown Action: " + strReceived)
    print(">>>Ignoring Unknown Action<<<")
    _response("  >>> " + strReceived + " is an Unknown Command and is Ignored. <<<<" )
    DEBUG("_unknownAction() exit\n")


# send response to commands
def _response(msg):
    DEBUG("\n_response() entry")
    logActions("Responding with msg: " + msg) 
    date = subprocess.check_output('date').decode('ascii')
    response = 'mosquitto_pub -h ' + MQTT_SERVER + ' -t ' + '\"' + MQTT_TOPIC_PUBLISH + '\" -m \"App: mqttController; Nodename: ' + NODENAME + ' Message: ' + msg + ' ' + date + '\"'
    os.system(response)
    DEBUG("\n_response() exit")


# ignore any received NODENAME message
def _nodename(strReceived):
    DEBUG("\nnodename() entry")
    logActions("Ignoring  NODENAME Action as it is just an echo of an echo!")
    print(">>>Ignoring NODENAME Action<<<")
    DEBUG("nodename() exit\n")


#  ================code to connect and receive mqtt messages===============


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


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)

# announce start
_response("\n\n>>> STARTED.  Runnning " + MQTT_CONTROLLER_VERSION + " <<<")
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
