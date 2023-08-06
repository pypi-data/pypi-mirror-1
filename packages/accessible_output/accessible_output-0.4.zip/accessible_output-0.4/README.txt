=====================================================
 The accessible_output library
=====================================================

:Author: Christopher Toth <Q@Qwitter-Client.net>
:Date: $Date: 03-10-2010 02:49:00 -0500 (Wed, Mar 10, 2010)
:Web site: http://www.qwitter-client.net/
:Copyright: 2010


.. contents::

============
Introduction
============

Accessible Output provides a standard way for developers to output text in either speech or braille using a preinstalled screen reader.  Using accessible_output makes creating self-voicing applications extremely easy.  

===========
Basic Usage
===========
Using accessible output is extremely simple::

    #!/usr/bin/env python
    from accessible_output import speech
    s = speech.Speaker() #Will load the default speaker.
    s.output("The message to speak")

==============
Speech Outputs
==============

* JAWS for Windows
* Window Eyes
* NVDA
* System Access and System Access To Go
* Microsoft sapi 5 speech


===============
Braille Outputs
===============


* JAWS for Windows
* Window Eyes
* NVDA
* System Access and System Access To Go
