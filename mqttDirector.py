import paho.mqtt.client as mqtt
import os
import subprocess
 
MQTT_SERVER = "192.168.1.208" #Hottub mqtt server/broker
MQTT_TOPIC_SUBSCRIBE = "CONTROLLER/ACTION"
MQTT_TOPIC_PUBLISH   = "CONTROLLER/RESPONSE"
NODENAME=os.uname().nodename  
LOG_FILE = "mqttActions.txt"  #a logging file

def DEBUG(msg):
    if  __debug__: 
        print(msg)

#log actions
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
    print("shutdown        Shutdown all systems.")
    print("reboot          Reboot all systems.")
    print("echo            Echo will cause all systems to reply with their hostname")
    print("blink <RPI>     Blink specified RPI (e.g., blink RPI-DEV) to blink for 1 minute.")
    print("newLog          NewLog will create new logging file, and increment existing to version +1")
    print("help         Help displays commands that can be invoked")
    print()
    print("exit         Exit this programe only; subscribers still monitoring MQTT Topic CONTROLLER/ACTION")
    print()
    command = str.upper(input("Please enter your command: "))
    print("Command received: " + command)
    print()

    _action(command)
    _menu()



#determine the appropriate control action contained in mqtt message
def _action(strReceived):
    DEBUG("\n_action() entry, strReceived: "+ strReceived)
    if (strReceived.find('SHUTDOWN') != -1):
        shutdown()
    elif (strReceived.find('REBOOT') != -1):
        reboot()
    elif (strReceived.find('ECHO') != -1):
        echo()
    elif (strReceived.find('BLINK') != -1):
        _blink_on(strReceived)
    elif (strReceived.find('NEWLOG') != -1):
        newLog()
    elif (strReceived.find('NODENAME') != -1): #!!!!!!!!!is this used?
        _nodename(strReceived)
    elif (strReceived.find('HELP') != -1):
        help()
    elif (strReceived.find('EXIT') != -1):
        exit()
    else:
        _unknownAction(strReceived);
    DEBUG("_action() exit\n")

# sends command via MQTT to Topic:Command
def _sendCommand(command):
    DEBUG("\n_sendCommand() entry")
    print("Sending command: " + command)
    date = subprocess.check_output('date').decode('ascii')
    response = 'mosquitto_pub -h ' + MQTT_SERVER + ' -t ' + '\"' + MQTT_TOPIC_SUBSCRIBE + '\" -m \"Nodename: ' + NODENAME + ' ' + command + ' ' + date  + '\"' 
    os.system(response)
    
    _response(command)
    DEBUG("\n_sendCommand() exit")
 
  
# shutdown():
def shutdown():
    msg=">>>> shutdown <<<<"
    DEBUG("\nshutdown() entry")
    logActions("Shutdown")
    print(msg)
    _sendCommand("SHUTDOWN")
    _response(msg)
    DEBUG("shutdown() exit\n")

#reboot the system
def reboot():
    msg=">>>> rebooting <<<<"
    DEBUG("\nreboot() entry") 
    logActions("Reboot")
    print(">>>rebooting<<<")
    _sendCommand("REBOOT")
    _response(msg)
    DEBUG("reboot() exit\n")

#echoo a message, specific to this instance,  back to the controller
def echo():
    msg = " >>> Online and Functioning. <<<<"

    DEBUG("\necho() entry")
    logActions("echoing this node name back to mqtt server")
    _sendCommand("ECHO")
    _response(msg)
    DEBUG("echo() exit")

#blink onboard led
def _blink_on(strReceived):
    msg = " >>> BLINKING LED <<<<"

    DEBUG("\n_blink_on() entry")
    logActions("Blinking LED on specified Node")
    _sendCommand(strReceived)
    _response(msg)
    DEBUG("echo() exit")


#refresh the log.  Keep 5 version
def newLog():
    msg = " >>>> Creating New Log, and bumping old versions +1 <<<<"
    DEBUG("\nnewLog() entry")
    '''
    os.system("mv ~/MySoftwareProjects/mqttController/mqttActions.txt4 ~/MySoftwareProjects/mqttController/mqttActions.txt5")
    os.system("mv ~/MySoftwareProjects/mqttController/mqttActions.txt3 ~/MySoftwareProjects/mqttController/mqttActions.txt4")
    os.system("mv ~/MySoftwareProjects/mqttController/mqttActions.txt2 ~/MySoftwareProjects/mqttController/mqttActions.txt3")
    os.system("mv ~/MySoftwareProjects/mqttController/mqttActions.txt ~/MySoftwareProjects/mqttController/mqttActions.txt2")
    
    os.system("echo -n \"New log started: \" > ~/MySoftwareProjects/mqttActions.txt")
    os.system("date >> ~/MySoftwareProjects/mqttActions.txt")
   
   '''

    _sendCommand("NEWLOG")
    _response(msg)
    print("Created new logging file and incrementing old versions to +1.")
    DEBUG("newLog() exit")

#help - list the known commands and etc
def help():
    msg=">>>> help <<<<"
    DEBUG("\nhelp() entry")
    logActions("Replying to 'help' request")
    
    print("\nCommands recognized for MQTT topic " + MQTT_TOPIC_SUBSCRIBE + ":")
    print("\tshutdown   - shuts all participating systems down.")
    print("\treboot     - reboots all participating systems.")
    print("\techo       - send an echo response to topic: " + MQTT_TOPIC_PUBLISH)
    print("\tnewLog     - increments all logs; creates and uses new log")
    print("\thelp       - lists the commands, etc.")
    print()

    _response(msg)
    DEBUG("\nhelp() exit")

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
