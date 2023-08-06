
Introduction
============

This is a distutils packaged version of the beatbox module by Simon Fell:
http://www.pocketsoap.com/beatbox/

This module contains 2 versions of the Salesforce client. XMLClient 
which is the original beatbox version of the client which returns
xmltramp objects and PythonClient which returns dicts with proper
python data types. ie integer fields return integers.

The PythonClient has all of the same methods as the XMLClient except
for describeLayout.

Another difference for the PythonClient is a change to the method signature of
query. Instead of a single query string it takes 2-3 arguments. A comma
seperated list of field names, the sObjectType and an optional 
conditionExpression. So if the original query was::

    "select FirstName, LastName from Contact where LastName = 'Doe'"

the new call to query would be::

    query('FirstName, LastName', 'Contact', "LastName = 'Doe'"

Compatibility
=============

Beatbox supports version 7.0 of the Salesforce Partner Web Services
API.

Examples
========

The examples folder contains the examples for the original beatbox. For
examples on how to use the PythonClient see
src/beatbox/tests/test_pythonClient.py.

Running Tests
=============

First, we need to add some custom fields to the Contacts object in your Salesforce instance:

 * Login to your Salesforce.com instance
 * Browse to Setup --> Customize --> Contacts --> Fields --> "New" button
 * Add a Picklist (multi-select) labeled "Favorite Fruit", then add
    * Apple
    * Orange
    * Pear
 * Leave default of 3 lines and field name should default to "Favorite_Fruit"
 * Add a Number labeled "Favorite Integer", with 18 places, 0 decimal places
 * Add a Number labeled "Favorite Float", with 13 places, 5 decimal places

Create a sfconfig file in your python path with the following format::

    USERNAME='your salesforce username'
    PASSWORD='your salesforce passwordTOKEN'

where TOKEN is your Salesforce API login token.

Add './src' to your PYTHONPATH

Run the tests::

    python src/beatbox/tests/test_beatbox.py
    python src/beatbox/tests/test_pythonClient.py

