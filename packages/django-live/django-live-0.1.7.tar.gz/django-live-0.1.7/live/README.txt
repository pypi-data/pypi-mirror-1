Author: NicoEchaniz (nico@rakar.com)


django-live is a little application packaged for Django that adds comet(push) based chat capabilities to your project.

The two current main features are:
- live help -> similar to PHPLive or HumanClick (only the chat functionality implemented so far)
- public chat rooms -> self explanatiry



Requirements
============

You need orbited>=0.7 [0] installed and you need to run either morbid (orbited's STOMP queue manager) or RabbitMQ[1] with it's stomp-adapter properly configured. Other options, like ActiveMQ have not been tested yet.


Setup
=====

Orbited
-------

You need to set up your orbited.cfg file to allow access to your STOMP broker port.
You could add, for example (that's the standard port):
[access]
* -> localhost:61613

if you are accessing the orbited server through a public domain, you will need to change this to something like:
* -> yourdomain.com:61613

If you choose to use morbid you may uncomment the stomp line in the orbited.cfg file to have it run automatically. You will also need to change the default orbited port if you will be running Django's web server on port 8000. Don't do this if you'll be using RabbitMQ.

[listen]
http://:9000
stomp://:61613  


Django
------

In your project settings.py you will need to add these settings (use your values):

ORBITED_HOST = "localhost" # or yourdomain.com
ORBITED_PORT = "9000"
STOMP_PORT = "61613"
STOMP_BROKER = "morbid" # accepts values "morbid" or "rabbitmq"

You will also need to add live to your INSTALLED_APPS

And edit your project's urls.py to include live.urls.
For example, you could add this line:

   (r'live/', include('live.urls')),



Usage
=====

Please consider that the current version is pretty rudimentary.

Asuming you have used the sample lines above, you may access de diferent features like this:

Open an anonymous chat channel using (alla humanclick):
yourdomain.com:8000/live/chat

The generated channel name will be visible to the manager, who will be able to asist the guest by clicking on the corresponding channel link.

Monitor open chat channels using:
yourdomain.com:8000/live/manage

Open or join the "public" chat room:
yourdomain.com:8000/live/public

Open or join a named public chat room:
yourdomain.com:8000/live/public/room_name


That's it so far.


This has been developed in less than 24hs as practice to learn Orbited, so feel free to write me with suggestions.




[0]http://www.orbited.org
[1]http://www.rabbitmq.com
