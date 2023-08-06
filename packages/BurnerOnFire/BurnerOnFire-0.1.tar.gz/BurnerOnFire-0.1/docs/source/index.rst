.. BurnerOnFire documentation master file, created by
   sphinx-quickstart on Sat Jul 25 13:04:04 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

:mod:`burneronfire` -- BurnerOnFire documentation
=================================================

.. highlight:: bash
.. module:: burneronfire
	 :synopsis: CLI/GUI program with main goal: to write same content to multiple burners at once

.. moduleauthor:: Domen Kozar & Jozko Skrablin

:Author: Domen Kožar <domenNO@SPAMdev.si>
:Graphic Design: Peter Čuhalev <peterNO@SPAMyukaii.com>
:Idea & Mentoring: Jožko Škrablin <daedalusNO@SPAMkiberpipa.org>
:Source: `bitbucket.org <http://bitbucket.org/iElectric/burneronfire>`_
:Bug tracker: `bitbucket.org - issues <http://bitbucket.org/iElectric/burneronfire/issues>`_
:Version: |release|
:License: BSD
:Platform: Unix-like systems


.. topic:: Overview

	 **BurnerOnFire** is multi-threaded program that can write same content (iso files for now) to multiple CD/DVD burners simultaneously. It is developed and tested only on Debian for now.

	 It uses D-Bus/HAL specification to interact with hardware.
	 It spawns subprocesses that wrap around command line program `Wodim <http://en.wikipedia.org/wiki/Cdrkit>`_. **BurnerOnFire** has both CLI and GUI(GTK+) interfaces.

	 This project was initially developed for `Club K4 <http://www.klubk4.org/>`_ by `kiberpipa.org <http://www.kiberpipa.org>`_ folks.

.. note::
	 **BurnerOnFire** passes arguments forward to Wodim, eg.: ``burneronfire -- -dummy`` simulates writing.


Installation
============

First of all, you need to install **python dbus bindings** and **python GTK2 bindings**, on Ubuntu::
	
	$ sudo aptitude install python-gtk2
	$ sudo aptitude install python-dbus

You are almost finished, run::

	$ wget http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c9.tar.gz#md5=3864c01d9c719c8924c455714492295e
	$ tar xf setuptools-0.6c9.tar.gz
	$ cd setuptools-0.6c9
	$ sudo python setup.py install
	$ sudo easy_install burneronfire
	$ burneronfire


Notes
=====

- **BurnerOnFire** lets `Wodim` handle everything concerned about burning.
- **BurnerOnFire** will save logs to current directory (currently all output from burners is logged).
- For debugging logging level, `BOF_DEBUG` environment variable is checked against value of 1.
- If `--limit or -l` parameter is passed, **BurnerOnFire** will try it's best to burn only specified number of discs. If burner will fail, it will wait for another empty disc to be inserted. 
- Write speeds are detected from all blank discs in burners. Flowchart for detecting write speeds can be found `here <_static/flowchart.jpg>`_.

Permissions
===========

- run with sudo to be able to lock memory
- run with sudo / make sure user is in cdrom group to be able to eject / close tray.

.. note:: If you receive "Operation not permitted", it means that current user does not have permissions to lock memory. This does not affect functionality of burning. To avoid such troubles, run **BurnerOnFire** with sudo.


Command line interface
======================

If **BurnerOnFire** is invoked with ``--filename or -f`` parameter, CLI interface is used::

	$ burneronfire --help
	Usage: burneronfire -s [write speed] -f [filename/path to filename] -m [burnmode]
			
		If no filename is given, GUI will start.
			
	Options:
		-h, --help                         show this help message and exit
		-f FILENAME, --filename=FILENAME   specify which file to burn
		-s BURNSPEED, --speed=BURNSPEED    specify burning speed (default is 16)
		-m BURNMODE, --mode=BURNMODE       provide write mode (defaults to DAO)
		-l LIMIT, --limit=LIMIT            number of discs to burn (defaults to 0, which means unlimited) 

Logging is used while burning, stdout/stderr are written to files in current directory::

	$ burneronfire -f test.iso 
	2009-07-25 13:40:41,717 - INFO: Starting!
	2009-07-25 13:40:55,378 - INFO: Empty disc inserted in burner DVDRAM GSA-T50L
	2009-07-25 13:40:55,378 - INFO: Burning... wodim driveropts=burnfree dev=/dev/sr0 fs=14M -eject -overburn -v -dao speed=16 test.iso
	2009-07-25 13:41:42,783 - ERROR: wodim: Operation not permitted. Warning: Cannot raise RLIMIT_MEMLOCK limits.scsidev: '/dev/sr0'
	devname: '/dev/sr0'
	scsibus: -2 target: -2 lun: -2
	Linux sg driver version: 3.5.27
	Wodim version: 1.1.9
	SCSI buffer size: 64512
	Beginning DMA speed test. Set CDR_NODMATEST environment variable if device
	communication breaks or freezes immediately after that.
	Speed set to 2822 KB/s
	wodim: fifo had 1 puts and 1 gets.
	wodim: fifo was 0 times empty and 0 times full, min fill was 100%.

Graphical interface
===================

.. image:: gui_main.png


TODO
====

- Implement *mode* to burn great amount of ISO's from a directory.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
