Environments
=====================================
 
Environments are the base elements of Doboz_web.

========================
General Environment manipulation
================================
Environment ids start with an index of 1

Resource path:
serverUrl/rest/environments
Valid content types:
"application/pollapli.environmentList+json" 

====
GET
====
url params/selection:
environements can be either gotten as a whole (no params)
or selected based on:
* status (active/inactive)
* id
Response content type: 
Json:"application/pollapli.environmentList+json" 

Response http status code: 200

====
POST
====
this is used to add a new environment to the system
request body params: 
name
description
status

Response: the selected representation of the added environment

Response content type:
Json: "application/pollapli.environment+json" 

Response http status code: 201

====
PUT
====
Not implemented

======
DELETE
======
this method clears the environement list completely
BEWARE!!! this deletes EVERY element !

Response: empty
Response http status code: 200


Single Environment manipulation
================================
Resource path:
serverUrl/environments/id

====
GET
====
Response content type: 
Json: "application/pollapli.environment+json" 
Other formats: not supported

Response http status code: 200

====
POST
====
Not implemented

====
PUT
====

Response content type:
Json: "application/pollapli.environment+json" 

Response http status code: 200

======
DELETE
======
Response: empty
Response http status code: 200


