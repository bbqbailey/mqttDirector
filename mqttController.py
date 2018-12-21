#!/usr/bin/python3
import paho.mqtt.client as mqtt
import os
import subprocess
import time
 
MQTT_SERVER = "192.168.1.208" #Hottub mqtt server/broker
MQTT_TOPIC_SUBSCRIBE = "CONTROLLER/ACTION"
MQTT_TOPIC_PUBLISH   = "CONTROLLER/RESPONSE"
NODENAME=os.uname().nodename  
LOG_FILE = "/media/Hottub/mqttActions.txt"  #a logging file

def DEBUG(msg):
    if  __debug__: 
        print(msg)

#log actions
def logActions(action):
#    os.system("echo -n \"" + action + ": \" >> mqttActions.txt")
    os.system("echo -n \"" + action + ": \" >> " + LOG_FILE)
#    os.system("date >> mqttActions.txt")
    os.system("date >> " + LOG_FILE)

#determine the appropriate control action contained in mqtt message
def _action(strReceived):
    DEBUG("\n_action() entry, strReceived: "+ strReceived)
    if (strReceived.find('REBOOT') != -1):
        reboot()
    elif (strReceived.find('SHUTDOWN') != -1):
        shutdown()
    elif (strReceived.find('NEWLOG') != -1):
        newLog()
    elif (strReceived.find('ECHO') != -1):
        echo()
    elif (strReceived.find('BLINK') != -1):
        _blink_on(strReceived)

#    elif (strReceived.find('NODENAME') != -1):
#        _nodename(strReceived)
    else:
        _unknownAction(strReceived);
    DEBUG("_action() exit\n")


# shutdown():
def shutdown():
    msg=">>>> shutdown <<<<"
    DEBUG("\nshutdown() entry")
    logActions("Shutdown")
    print(msg)
    _response(msg)
    DEBUG("shutdown() exit\n")

    os.system("sudo shutdown")

#reboot the system
def reboot():
    msg=">>>> rebooting <<<<"
    DEBUG("\nreboot() entry") 
    logActions("Reboot")
    print(">>>rebooting<<<")
    _response(msg)
    DEBUG("reboot() exit\n")

    os.system("sudo reboot")

#echoo a message, specific to this instance,  back to the controller
def echo():
    msg = " >>> Online and Functioning. <<<<"

    DEBUG("\necho() entry")
    logActions("echoing this node name back to mqtt server")
    _response(msg)
    DEBUG("echo() exit")

#Blinking On - sometimes I'm not sure which RPI I need to disconnect.
#   sending a blinking_on command to just this RPI will provide capability
#   blink 60 times.
#   Before returning, will set the led mode to cpu0
def _blink_on(strReceived):
    strReceived = strReceived.upper()
    nodename=NODENAME.upper()
    DEBUG("\n_blinking_on() entry, strReceived: " + strReceived)
    logActions("Blinking " + nodename)
    _response("Blinking " + nodename)

    #determine if I'm the RPI that needs to blink
    if (strReceived.find(nodename) != -1):
        DEBUG("_blinking_on(): activated for me! ")
        for x in range(1, 60):
            #turn led on for 1/4 sec
            os.system("echo 1 | sudo tee /sys/class/leds/led1/brightness 1>/dev/null")
            time.sleep(0.25) # pause (sleep) for 1/4 second
            #turn led off for 1/4 sec
            os.system("echo 0 | sudo tee /sys/class/leds/led1/brightness 1>/dev/null")
            time.sleep(0.25)
        #return to normal operation
        os.system("echo cpu0 | sudo tee /sys/class/leds/led1/trigger")
    else:
        DEBUG("\n_blinking_on(): was not requesting me: " + nodename)

    DEBUG("_blinking_on() exit\n")
  
#refresh the log.  Keep 5 version
def newLog():
    msg = " >>>> Creating New Log, and bumping old versions +1 <<<<"
    DEBUG("\nnewLog() entry")

    os.system("mv ~/MySoftwareProjects/mqttController/mqttActions.txt4 ~/MySoftwareProjects/mqttController/mqttActions.txt5")
    os.system("mv ~/MySoftwareProjects/mqttController/mqttActions.txt3 ~/MySoftwareProjects/mqttController/mqttActions.txt4")
    os.system("mv ~/MySoftwareProjects/mqttController/mqttActions.txt2 ~/MySoftwareProjects/mqttController/mqttActions.txt3")
    os.system("mv ~/MySoftwareProjects/mqttController/mqttActions.txt ~/MySoftwareProjects/mqttController/mqttActions.txt2")
    
    os.system("echo -n \"New log started: \" > ~/MySoftwareProjects/mqttActions.txt")
    os.system("date >> ~/MySoftwareProjects/mqttActions.txt")

    _response(msg)
    print("Created new logging file and incrementing old versions to +1.")
    DEBUG("newLog() exit")

# deal with unknown command actions received def unknownAction(msg):
def _unknownAction(strReceived):
    msg=">>>> Unknown Action Requested <<<<"
    DEBUG("\n_unknownAction() entry")
    logActions("Ignoring Unknown Action: " + strReceived)
    print(">>>Ignoring Unknown Action<<<")
    _response("  >>> " + strReceived + " is an Unknown Command and is Ignored. <<<<" )
    DEBUG("_unknownAction() exit\n")

#send response to commands
def _response(msg):
    DEBUG("\nresponse() entry")
    logActions("Responding with msg: " + msg) 
    date = subprocess.check_output('date').decode('ascii')
    response = 'mosquitto_pub -h ' + MQTT_SERVER + ' -t ' + '\"' + MQTT_TOPIC_PUBLISH + '\" -m \"Nodename: ' + NODENAME + ' ' + msg + ' ' + date  + '\"' 
    os.system(response)
    DEBUG("\nresponse() exit")

#ignore any received NODENAME message
def _nodename(strReceived):
    DEBUG("\nnodename() entry") 
    logActions("Ignoring  NODENAME Action as it is just an echo of an echo!") 
    print(">>>Ignoring NODENAME Action<<<")
    DEBUG("nodename() exit\n")



#================code to connect and receive mqtt messages===============

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    DEBUG("\non_connect() entry")
    print(" Connected with result code "+str(rc))
    logActions("\n>>>Connected with result code<<<" +str(rc))
 
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

#announce start
_response(">>> STARTED <<<")
 
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
