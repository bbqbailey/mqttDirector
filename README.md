# The MQTT Mosquitto System Controller

I have multiple computer systems in my office, mostly Linux of some description.

Currently, there are two (2) large Ubuntu systems, plus 10 or more Raspberry
Pi (RPI) systems.  Normally, all of these are up 24/7.

I have a UPS that feeds the main computers and RPIs, so I'm fairly
insulated from electrical issues, except for thunderstorms.  Lightning can
be jumping 30,000 feet, so I've not found any device that can isolate all
of the lightning if it hits close to my home.

For that reason, when a thunder storm starts coming close to my home, I shutdown 
and unplug my computer systems.  It's important, since these are all some flavor
of Linux, that I shut them down using the system 'shutdown' command, instead
of just unplugging the power.

This is also the requirement for instances when I'm away and we lose electricty
for some reason, and then the UPS battery gradually loses power, until it 
drops the power to the systems.

The UPS I have will send a shutdown signal to the system that monitors it.  But
I wanted it to also feed all of the other systems, including the RPIs.

When a thunderstomr is coming, or the UPS battery is starting to reach its limit
I'm currently having to manually log into each of these systems, then invoke a 
'shutdown' command.  This can take a while with all of the systems ....

So, I wanted something that would allow me to send a shutdown command to all of
the systems.

This is that system!

It uses MQTT Mosquitto, with a broker/server running on my main system.  Then all 
of the RPIs and other systems subscribe to the CONTROL topic, taking action
as defined in the message or payload.

The Linux 'shutdown' command is protected, so that users are required to have
'sudo' priviliges in order to invoke the command.  However, the normal function
of the Linux system is to require 'authentication' for using 'sudo', which
means any script that invokes 'shutdown' will also be prompted for a password
for authentication.

This is not how I want this to work.  Therefore, a change has to be made to the
/etc/sudoers file, preferrabley in /etc/sudoers/sudoers.d/010_pi-nopasswd file.

The added line required is:
	pi RPI-Dev =NOPASSWD: /sbin/reboot

When invoked via the Python3 os.system command, it is required to be "sudo shutdown now".

I don't typically use any delay on the 'shutdown now', because typically I'm rather 
desperate to get the systems down!
