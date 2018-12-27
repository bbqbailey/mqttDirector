--- OVERVIEW ---

Files:
    mqttDirector.py 
        A python program that sends commands to systems 
        listening for these commands.

    mqttController.py 
        A python program that runs as a service, lisetning
        for commands issued by mqttDirector on the network.
        The commands arrive via a MQTT Mosquitto topic.

    mqttController.service
        A systemd file that runs on the same node where the 
        mqttController.py will run.  This starts the service
        mqttController.py on reboot or startin of the system.

    mqttMonitorRPIChannels
        A simple 'bash' file that monitors the MQTT  topics
        that are published by MqttDirector.

    mqttAction.txt  
        This is a log file that is created in the same  
        location where mqttcontroller.py exists.

Commands Currently Recognized

        Reboot: causes all RPIs to reboot:
        
        Shutdown: causes all RPIs to shutdown 

        Echo: All RPIs to reply with an echo with a timestamp

        Blink <RPI>: Causes the onboard LED to blink.  Helpful
            in locating a particular RPI in a stack of RPIs.

        NewLog: Roll the logs of mqttAction.txt, keeping a 
            copy of no more than five.

        Version: Causes the RPIs to respond with the version of the 
            software mqttController.py that is running.

        osRelease: Causes RPIs to respond with the OS Version they 
            are running.  Lists the contents of /etc/os-release.

Future Intended Changes:
        
       
        Provide a crontab entry to refresh the mqttAction.txt 
        logs.  Currently they are manually refreshed via the 
        menu option 'newLog' invoked by the MqttDirector.  It 
        keeps a maximum of 5 versions.


Notes:

        It should be noted that while the primary recepients via 
        mqttController of commands issued by MqttDirector are 
        RPIs, any Linux system running mqttController, with appropriate
        'sudo' privilidges should be able to respond.

        The design of this program is to provide for future 
        growth of commands that can be invoked on the various
        network attached RPIs.

        All commands received in mqttController, are logged in 
        mqttAction.txt.  The entries include the node names, and the 
        timestamp of the system generating the entry.
        

--- Background ---

I needed a way to quickly bring down multiple Raspberry PIs (RPI)
on my home network.  Doing it manuaully, in the case where a 
thunderstorm is quickly approaching, took too much time to login 
to each, then issue the shutdown commands.

So I implemented a MqttDirector python program that would allow me 
to issue commands to the networked RPIs.  These commands would be 
transported from my main computer, where mqttDirector was running,
to each RPI using MQTT Mosquitto for the transport.

Each RPI was running an instance of mqttController, which was a 
python program that listens for commands from MqttDirector by 
listening for commands from MQTT Mosquitto.

Note: I wrote this for myself, to install from my development node.
In this document, I'll refer to it as the node DEV_NODE.
So the references to DEV_NODE should be changed by you
to reflect your development machine.  Likewise, I'm referring to the 
user id as USER.

I would therefore, in order
to keep the instructions in synch with your usage, create on your
development machine, the directory structure ~/MySofwareProjects/mqttController
Then you can pull from github.com/bbqbailey/mqttDirector and place into 
your new ~/MySoftwareProjects/mqttController.  Then substitute
your node's name for DEV_NODE and you should be good to go.

Note: The mqttDirector.py should run on your development node; the
mqttController.py should run on the RPIs you want to control.

Note: This has only been tested on RPI Raspbian versions Jessie and Stretch
While it may work on other versions, it is your responsibility to verify
this.


There are two (2) applications that together will control a RPI via
messages received communicated via MQTT Mosquitto.

The two applications are: mqttDirector, and mqttController.

--- MqttDirector.py INSIGHT ---
Requires python3

mqttDirector sends requests to mqttController.  mqttcontroller then
performs the requested action.  It primarily will run on node DEV_NODE.

The requests for action are transported from the mqttDirector to the
mqttController via an MQTT Moquitto broker.

mqttDirector utilizes the MQTT Mosquitto Server (or Broker - an older 
terminology), which has to be installed on DEV_NODE and run as a service.  
Please refer to MQTT Mosquitto for more information as to installing 
and setting up the MQTT Mosquitto server.

mqttDirector is a terminal-based assplication, and has a simple text-based 
menu enterface.

Running mqttDirector will present a menu of choices.  E.g., 'echo', when 
entered as the menu command, will cause all RPIs that are listening to the
mqttDirector, to reply with their nodename.

The MQTT Topics utilized are:

    CONTROLLER/ACTION
        Commands sent from mqttDirector are sent with Topic CONTROLLER/ACTION

    CONTROLLER/RESPONSE
        Responses from mqttController are sent with Topic CONTROLLER/RESPONSE

    CONTROLLER/#
        Enables you to monitor both 'channels'.
        The utility mqttMonitorRPIChannels will do this for you.

The mqttDirector menu command 'help' will list the available commands.



--- mqttController.py INSIGHT ---
Requires python3

It typically will run on a Raspberry Pi device, as user 'pi'.  It can be run 
as a standalone application but the primary use is that of a systemd service.
When running as a systemd service, the output will not be visable from a 
terminal, as there is no terminal associated with the service; instead, the 
information can be viewed in the log file /home/pi/mqttController/mqttAction.txt.

Multiple versions of this log file can be created by invoking the mqttDirector
command 'newLog', with a maximum of 5 iterations being retained.

--- mqttMonitorRPIChannels INSIGHT ---

The bash utility mqttMonitorRPIChannels allows the monitoring of both channels, 
CONTROLLER/ACTION and CONTROLLER/RESPONSE.  It can be redirected to a
file when starting it.  It is located on DEV_NODE in directory .../mqttDirector


SETUP:
In order to run the python application mqttDirector, several things must
be set up first; it is also dependent on the application mqttController
to run the commands on a RPI via MQTT Mosquitto.

Please perform the following commands, in order, on the RPI that will be 
utilized for mqttController.

0.  It would be best if we started with your RPI being at the latest code level.  
    So exicute the following:

        sudo apt-get update

    if no errors, then execute:

        sudo apt-get upgrade

1.  Install paho-mqtt.
    This provides python the ability to communicate via MQTT.
    Reference: https://pypi.org/project/paho-mqtt

    Issue the following pip3 install command:
    
        sudo pip3 install paho-mqtt

    If you get an error,  you may not have pip3 installed.  
    To install pip3, issue the following command:

        sudo apt install python3-pip

    Then retry the 'sudo pip3 install paho-mqtt' command above.

    

2.  mqttController.py 
    Invokes commands received from mqttDirector.
    Commands, such as to shutdown or reboot the RPI, among others.  
    Some of these commands require root privilidges (e.g., shutdown, reboog), 
    making use of the 'sudo' command. 'sudo' requires authentication, 
    in the form of a login password.  This is not convenient while running 
    the application.  Therefore, the following changes will need to be made 
    to the file: /etc/sudoers.d/010_pi-nopasswd

    The following will setup subdoers to allow user 'pi' to issue these commands.

    2.1.1 Change to /ect/sudoers.d

        cd /etc/sudoers.d

    2.1.2 Make a copy of suduoers.d/010_pi-nonpasswd.  It is protected, so use 'sudo'

        sudo cp 010_pi-nopasswd 010_pi-nopasswd.original

    2.1.3 Now, using sudo, edit the 010_pi-nopasswd file
        e.g., 'sudo vim /010_pi_nopasswd'
        Edit 010_pi-nopasswd, and add the following two entries

        Assuming you are using 'vim' as your editor, issue the following:

            sudo vim 010_pi-nopasswd

        Now past the following two lines of text into your 010_pi_nopasswd file:

            pi RPI-Dev =NOPASSWD: /bin/systemctl poweroff,/bin/systemctl halt,/bin/systemctl reboot
            pi RPI-Dev =NOPASSWD: /sbin/reboot

        Save your work.
            Note: if vim says this is a read-only file, then save with the ':w!" option, then :q" to exit

        Verify 010_pi_nopasswd has the correct information in it now.
    
            sudo cat 010_pi-nopasswd

    2.2.    You may have to logout then login for it to work.  Or, if that doesn't work, 
            you may have to reboot.  You can test via 'sudo reboot', providing you haven't 
            already performed a sudo and authenticated while in this session.

3.  Assuming you have made changes outlined in section 2 above, and have tested it and it
    works properly, you can move on to the next step.

4.  DEV_NODE is the main system for development, but the mqttController will be running on a
    RPI.  Therefore, it is best to mount the development DEV_NODE into a directory located
    on the RPI, and then copy the required files to your /home/pi/MySoftwareProjects/mqttController.

    So, we are going to use 'ssfs' to mount the DEV_NODE's directory to the RPI's /media subdirectory.

    4.1  As pi, perform the following:

        4.1.1 cd to the RPI directory /media

            cd /media

        4.1.2 create the directory DEV_NODE.  This is where the DEV_NODE code will mount.  

            sudo mkdir DEV_NODE

        4.1.3 Directory DEV_NODE is probably owned by root, so you'll need to change it, but
            First, verify that it is owned by root by doing a 'ls -al' 

                ls -al /media

            If it is owned by 'root root', then you'll want to change it to pi pi by issuing:
            
                sudo chown pi:pi DEV_NODE

            Now ensure it is correct by doing ls -al /media and observing the ownserhip of pi pi

                ls -al /media 
            

        4.1.4 Now we are going to create a flag-file to show wherether DEV_NODE's directory
            has been mounted or not. Well do this by issueing the 'touch' command
            for a file named 'NOT_MOUNTED'.  If in the future you do a ls -al /media/DEV_NODE
            and you see the file 'NOT_MOUNTED', then you know your DEV_NODE file system has
            not been mounted, and you'll need to do the 'sshfs' command (down below).

                First, cd to the DEV_NODE directory you just created:

                    cd /media/DEV_NODE

                Now, using 'touch' create the file NOT_MOUNTED

                    touch NOT_MOUNTED

            Now, make sure you've created this file by doing ls -al

                    ls -al

            You should see the file NOT_MOUNTED in /media/DEV_NODE.

        4.1.5  The directory on DEV_NODE that contains the file mqttController.py, is located at
            /home/USER/MySoftwareProjects/mqttController/.  So we are going to mount this 
            directory at the mount point you just created: /media/DEV_NODE

            First, cd out of the /media/DEV_NODE directory
    
                cd ..

        4.1.6   Now verify the directory /home/pi/MySoftwareProjects/mqttController exists.

                ls -al ~/MySoftwareProjects/mqttController
                
            If it doesn't exist, then create it.

                mkdir ~/MySoftwareProjects
                mkdir ~/MySoftwareProjects/mqttController

            Now verify it was correctly created

                ls -al ~/MySoftwareProjects/mqttController

        4.1.7   Next, we'll sshfs the filesystem

                sshfs -o nonempty USER@DEV_NODE.local:./MySoftwareProjects/mqttController   /media/DEV_NODE

            Note: if your system complains that it does not have the command 'ssfs', then issue
            the following command to install, then repeat the 'sshfs' command above:

                sudo apt install sshfs

        4.1.8 Confirm that you have mounted the directory properly by performing 'ls -al'

                ls -al /media/DEV_NODE
            
            You should see many files, not the single file NOT_MOUNTED.


            Now cd to the directory where your code will be placed

                cd ~/MySoftwareProjects/mqttController

        4.1.9 We will copy the pythono program mqttController.py 
            from /media/DEV_NODE/  into ~/MySoftwareProjects/mqttController which is your 
            current directory from above.

            cp /media/DEV_NODE/mqttController.py ./

        4.1.10 Now we will copy the sytemctl service mqttController.service 
            from /media/DEV_NODE to ~/MySoftareProjects/mqttController
            
            cp /media/DEV_NODE/mqttController.service ./

        4.1.11 Do a 'ls -al' on ~/MySoftwareProjects/mqttController to ensure you see the two files:

            ls -al ~/MySoftwareProjects/mqttController

            shows: mqttController.py and mqttController.service

        4.1.12 If all has gone well, you can unmount the sshfs file system.
            
            sudo umount /media/DEV_NODE

            Verify the unmount:
                
                ls -al /media/DEV_NODE

            It should only show the NOT_MOUNTED file.

5.  mqttDirector and mqttController both use MQTT Moquitto Server (Broker is older terminalogy).
    We ill need to ensure this has been installed on your system, and is the correct version.

    Issue the vollowing command:

        which mosquitto_sub

    responds with: /usr/bin/mosquitto_sub

    If your system instead responds with nothing, then it's not installed.

    The instructions that follow are specific to your Raspbien OS version; make
    sure you are using the correct version, or you may experience problems!



    5.1 ============ For JESSIE  ================

        Note: these instructions are for a RPI Raspbian running version Jessie.  If you
        are running Stretch, then please skip these instructions, and advance to section
        "For Stretch"

        You can determine your Raspbian version by performing the following:

            cat /etc/os-release

        For questions, see: http://jakemakes.eu/installing-mqtt-brokermosquitto-on-raspberry-pi/
        Note: the text that follows is taken from jakemakes.eu above

            Add the Mosquitto repository:

            sudo wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key
            sudo apt-key add mosquitto-repo.gpg.key
            sudo rm mosquitto-repo.gpg.key
        
        Next, make the repository available to apt-get.  First we need to change to the apt
        sources list directory:
    
            cd /etc/apt/sources.list.d/

        Now install the packages list for your Raspbian

            sudo wget http://repo.mosquitto.org/debian/mosquitto-jessie.list

        Now update apt information and install Mosquitto

            sudo apt-get update
            sudo apt-get install mosquitto mosquitto 

        Now we can install the three parts of Mosquitto proper.
            - mosquitto - the MQTT broker/server
            - mosquitto-cliends - command line clients, very useful in debugging
            - python-mosquitto -the Python language bindings

            sudo apt-get install mosquitto mosquitto-clients python-mosquitto

        Now the broker is immediately started. Since we have to configure it first, 
        stop it by command:

            sudo /etc/init.d/mosquitto stop

        We need to set up the configuration file.  The configuration files is located at
        /etc/mosquitto.

        Edit the config file:

            sudo vim /etc/mosquitto/mosquitto.conf

        The file should look like this:

            # Place your local configuration in /etc/mosquitto/conf.d/
            #
            # A full description of the configuration file is at
            # /usr/share/doc/mosquitto/examples/mosquitto.conf.example

            pid_file /var/run/mosquitto.pid

            persistence true
            persistence_location /var/lib/mosquitto/

            log_dest file /var/log/mosquitto/mosquitto.log

            include_dir /etc/mosquitto/conf.d

        Change it to look like this:

            # Place your local configuration in /etc/mosquitto/conf.d/
            #
            # A full description of the configuration file is at
            # /usr/share/doc/mosquitto/examples/mosquitto.conf.example

            pid_file /var/run/mosquitto.pid

            persistence true
            persistence_location /var/lib/mosquitto/

            log_dest topic

            log_type error
            log_type warning
            log_type notice
            log_type information

            connection_messages true
            log_timestamp true

            include_dir /etc/mosquitto/conf.d
        
        Start the mosquitto server
    
            sudo /etc/init.d/mosquitto start

        Test the installation by opening 2 terminal windows to first insert:

            mosquitto_sub -d -t hello/world

        And to the second window, insert:

            mosquitto_pub -d -t hello/world -m "Hello from Terminal window 2!"

        When you have done the second statement you should see something similar to
        this in the Terminal 1 window:

            sudo mosquitto_sub -d -t hello/world
            Client mosqsub/3014-LightSwarm sending CONNECT
            Client mosqsub/3014-LightSwarm received CONNACK
            Client mosqsub/3014-LightSwarm sending SUBSCRIBE (Mid: 1, Topic: hello/world, QoS: 0)
            Client mosqsub/3014-LightSwarm received SUBACK
            Subscribed (mid: 1): 0
            Client mosqsub/3014-LightSwarm received PUBLISH (d0, q0, r0, m0, 'hello/world', ... (32 bytes))
            Greetings from Terminal window 2

    5.2 ============= For STRETCH ==============

        For questions, see:
            https://www.switchdoc.com/2018/02/tutorial-installing-and-testing-mosquitto-mqtt-on-raspberry-pi/

        To install mosquitto server, issue the following commands:

            sudo wget https://repo.mosquitto.org/debian/mosquitto-repo.gpg.key
            sudo apt-key add mosquitto-repo.gpg.key
            cd /etc/apt/sources.list.d/

            sudo wget http://repo.mosquitto.org/debian/mosquitto-stretch.list
            sudo apt update
            sudo apt upgrade


        Now we can install the three parts of Mosquitto proper.  For questions, see
            https://www.switchdoc.com/2018/02/tutorial-installing-and-testing-mosquitto-mqtt-on-raspberry-pi/

           sudo apt install mosquitto mosquitto-clients
           sudo apt install python-pip	
           sudo pip install paho-mqtt
    



6.  You will now need to install the mqttController.service onto your RPI so that it 
    will always provide the mqttController.py service without your having to manually
    start it in a terminal.

    First, make sure you are still in the ~/MySoftwareProjects/mqttController

        cd ~/MySoftwareProjects/mqttController

    Next, copy the mqttController.service to the systemd directory:
    
        sudo cp mqttController.service /lib/systemd/system/

    Next, 'enable' it so it will start any time the system starts back up

        sudo systemctl enable mqttController.service

    Next, 'daemon-reload' to insert it into the systemd without restarting

        sudo systemctl daemon-reload


7.  Your system should already have python 3.5 installed. Let's check; Ctrl-Z 
    will exit it.  Note: while Python 3.4.x may work, but I've experience
    some issues running 3.4 on Raspbien 'Jessie'.  It's certainly OK to install 
    under 3.4.x, but if you have any problems, I would 'suggest' moving to 
    3.5.x.  I can't guarentee that moving to 3.5.x won't impact other programs 
    you have installed; you should verify before installing.

        python3

    You should see some lines of text, with the last line showing ">>>".  If 
    you see this, then you should be good.  

    The version that I'm showing right now, and that the application was 
    developed and tested on, is Python 3.5.3 (this should be the first line 
    of the output from your 'python3' command.  If you don't see this, or 
    if you get an error trying to invoke 'python3', then you will need to 
    install python3.  Please perform a google search of Raspberry Pi python3' 
    and follow installation instructions.

    I tried updating one RPI system, which was running Python 3.4 on 'jessie' 
    using the following, but it did not upgrade Python 3.4 to 3.5:

        sudo apt update

    Then

        sudo apt upgrade
    
    Note: this may take a while, particularly the 'upgrade'
    
    Repeat the python3 command to see what version you are running if you did 
    the update and upgrade.

8.  Reboot your RPI to see if your service will auto-start:

        sudo reboot

9.  Once it has rebooted, then issue the following command to verify your service 
    is up and running:

        sudo systemctl status mqttController.service

10.  To test system should now be properly set up to run mqttDirector on your MQTT 
    Server system; mine is on DEV_NODE.

    So, from a terminal session on my DEV_NODE system, I cd 
    to ~/MySoftwareProjects/mqttDirector

        cd ~/MySoftwareProjects/mqttDirector

    Then issue the following command:

        python3 -O mqttDirector.py   (Note: this option -O surpresses debug output.  For the first run, I would suggest -O)

    or

        python3 mqttDirector.py      (Note: the lack of the -O option means debug info will be displayed.)

11.  If you have sucessfully completed the application installation, you should see the file 
    ~/MySoftwareProjects/mqttController/mqttAction.txt, which is the log file for the application.  
    You can create a new log file, while retaining up to 5 total files.  To do this, on DEV_NODE, from the
    application 'mqttDirector', issue the 'newLog' command.
            

Please let me know of any issues.
Thanks!  Ben Bailey, Dec 2018
