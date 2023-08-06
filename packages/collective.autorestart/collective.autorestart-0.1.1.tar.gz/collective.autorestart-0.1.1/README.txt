Automatically reload changed Python files - putting agility back to Plone development.

collective.autorestart monitors Python .py files for changes and triggers a reload when you edit the files. 
This way you don't need to restart Plone server between your code edit runs.
collective.autorestart uses `plone.reload <http://pypi.python.org/pypi/plone.reload/0.10>`_ package to perform the actual code replacement.

File system is monitored using inotify interface which is only available for Linux. 
The future versions will support other operating systems as long as somebody contributes the file system monitoring 
code or gives the author a new computer running operating system X.

Features
--------

* Recursively detect changes in ZCML and Python files which are known to Zope

* Automatically trigger reload when files are changed (saved)

* Audio playback depending on whether the restart succeed or failed - you can go back to your files and you don't need to watch the terminal

Dependencies
------------

* plone.reload

* pyinotify for monitoring files.

* pygame for audio playback (optional)

pyinotify relies on Linux kernel feature called inotify and thus
this application only works on Linux currently. However, it should be
trivial to port it for other platforms. 


Installation 
-------------

pyinotify depends on ctypes package and currently (04/2009) ctypes package is broken in PyPi. Manual installation needed::

	wget http://kent.dl.sourceforge.net/sourceforge/ctypes/ctypes-1.0.2.tar.gz
	tar -xzf ctypes-1.0.2.tar.gz 
	cd ctypes-1.0.2/
	python2.4 setup.py build
	sudo python2.4 setup.py install
	
	
Buildout setup
==============

Add the following egg to your buildout.cfg. 

	eggs =
		collective.autorestart
		
	...
	
	zcml = 
		collective.autorstart
		
Rerun buildout. 

Adding sound effect support
===========================

Optionally `pygame <http://www.pygame.org>`_ egg is needed for sound support. Pygame depends on SDL development library::

	sudo apt-get install libsdl1.2-dev libsdl-mixer1.2-dev 
	
Add the following egg to your buildout.cfg::

	eggs =
		pygame
		
Rerun buildout. Answer yes when pygame barks about missing libraries.

Usage
-----

Start Plone normally in the foreground using command::

	bin/instance fg 
		
collective.autorestart might not be effective immediately, since its sets the monitor on files on background.
When it starts, you'll see a message in your terminal::

	collective.autorestart Monitoring 3477 paths 12591 files for changes

Edit any Python files. When you press save you should output in your terminal::

	2009-04-15 04:11:37 INFO collective.autorestart Detected file system change:/home/moo/workspace/y-trunk/x/browser/views.py/
	2009-04-15 04:11:37 INFO collective.autorestart Reloading Plone
	2009-04-15 04:12:06 INFO collective.autorestart Reloaded done, report:Code reloaded:

		...x/browser/views.py	
				
If you have pygame installed you will also hear a sound effect depending on whether code reload succeeded or failed.
    
Knowns issues
-------------

- Sometimes Zope process seem to fall into Zombie state (kind of dead, but blocks the HTTP port). In this case, manually
  kill Zope.
  
- New files are not automatically picked up

- If you quickly edit and save several files some changes might go unnoticed

- ZCML support is currently disabled (bgthread.reload_plone) since it seems to break zope.schema vocabularies
  and the instance ends up to a broken state

- Something (some editors) are keen to fire double modify events on file changes

Author
------

Mikko Ohtamaa 

`Twinapex Research, Oulu, Finland <http://www.twinapex.com>`_ - High quality Python hackers for hire


