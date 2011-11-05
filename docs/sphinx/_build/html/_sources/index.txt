.. Doboz-web documentation master file, created by
   sphinx-quickstart on Thu Mar 24 10:21:55 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Doboz-web's documentation!
=====================================

.. warning::

   Currently (version 0.5.0) Pollapli is not even an alpha version, features and documentation are partially implemented
   and being reworked a lot, so use at your own risk! 
   
.. warning::

   Don't be surprised if you see both the names "Pollapli" and "DobozWeb" , Doboz Web is actually going to be part of the
   larger application called Pollapli, so in the transitionning phase , a lot of text will be bear reference to both! 
 
Are you a user?
===============
 
Pollapli was thought from the start with end-users (that is you !)  in mind, making it as easy to use as possible, 
without too much technical knowledge.



Contents:

.. toctree::
	:maxdepth: 2
	
	user_overview
	user_tutorial
	user_interface
	
Are you a developper? 
=====================
 
All the technical doodads, the apis, class and function and documentations can be found here.
 
.. note::

   Everything is still in developpment, therefore subject to change: for example the move to the Twisted
   framework was done recently,  so some older elements still remain, and some other things are still buggy
   (notably thanks to the wonky support for Serial ports provided by twisted, but i am working on that).
 
Contents:

.. toctree::
	:maxdepth: 2
   
	dev_overview
	run
	rest_api
	components
	tools

Main addOns / subprojects
=========================
* pollapli : reprap control and managment
* hydroduino : remote monitoring and  control of (hydroponic) gardens/ aquariums etc 


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

