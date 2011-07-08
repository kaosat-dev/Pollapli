Rest Api
=====================================
------------------------
Overview of the rest api
------------------------

The main (and only for now) way to communicate with the Pollapli server side is via a REST based api.

Contents:

.. toctree::
	:maxdepth: 2
   
	rest_api_environments


--------
Handlers
--------

.. automodule:: doboz_web.core.server.rest.handlers
	:members:
	:show-inheritance:


	
------------------------
Error codes / messages
------------------------
	Possible error http status codes/ application error codes/error messages:
	
	* ParameterParseException,400 ,1,"Params parse error"
  	* UnhandledContentTypeException,415 ,2,"Bad content type"
  	* EnvironmentAlreadyExists,409 ,3,"Environment already exists"
  	* EnvironmentNotFound,404 ,4,"Environment not found"
  	* UnknownNodeType,500 ,5,"Unknown node type"
  	* NodeNotFound,404 ,6,"Node not found"
  	* NoDriverSet,404,7,"Node has no connector" 
	

+-------------------------------+-----------+---------------------+-----------------------------+
| Exception Class               | Http code | Pollapli error code | Error Message               |
+===============================+===========+=====================+=============================+
| ParameterParseException       |   400     |         1           |"Params parse error"         |
+-------------------------------+-----------+---------------------+-----------------------------+
| UnhandledContentTypeException |   415     |         2           |"Bad content type"           |
+-------------------------------+-----------+---------------------+-----------------------------+
| EnvironmentAlreadyExists      |   409     |         3           |"Environment already exists" |
+-------------------------------+-----------+---------------------+-----------------------------+
| EnvironmentNotFound           |   404     |         4           |"Bad content type"           |
+-------------------------------+-----------+---------------------+-----------------------------+


   