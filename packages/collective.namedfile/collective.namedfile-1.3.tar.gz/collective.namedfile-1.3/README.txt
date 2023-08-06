Introduction
============

A correctly working File widget and field for zope.

The standard FileWidget returns a string instead of an IFile instance,
which means it will always fail schema validation in formlib.

In addition this widget will also extract the filename and Content-Type
from the request.

Copyright
=========

Copyright 2007 by Jarn AS
Copyright 2007 Laurence Rowe

Zope Public Licence 2.1

Credits
=======

Widget originally developed for Reflecto 
    `Jarn <http://www.jarn.com>`_,
    Wichert Akkerman, Martijn Pieters

Further enhancements  
    `Laurence Rowe <http://objectvibe.net/blog>`_,
    `Jens Klein <http://www.bluedynamics.com/>`_


