Drivers
=====================================

Drivers define **how** you connect a node to the system.

Drivers are made of two main components:

* a hardwareHandler for all lower level manipulation(for example serial etc) connecting/disconneting, and in/out formatting of the raw data via a protocol
* a logicHandler for all higher level functions : such as a queue system etc
A driver sends events/signals to all its listeners (somewhat like a software base interupt system) and acts as a main
access point for all its subelements (other systems and components talk to then driver, not its subcomponents)
 
Contents:

.. toctree::
   :maxdepth: 2


.. automodule:: pollapli.core.components.drivers
 :members:
 :show-inheritance:
 