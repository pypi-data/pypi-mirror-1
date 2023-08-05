# Release information about tg_interface

version = "1.2-0.01"
description = "interface.js javascript library for TurboGears"
long_description = """

Install
==============
Use setuptools to install::
    
    $easy_install tg_interface

Details
==============
While I really like the jQuery library, it lacks a lot
of pretty plugins like you can get with dojo, scriptaculous
or the likes. In order to remedy this problem, I have created
a quick and dirty wrapper for the fantastic "interface.js",
available here:

http://interface.eyecon.ro/download

This library just installs interface, so the best place to put
it is in the tg_include_widgets location described below, right
AFTER the jquery.jquery definition.


Usage
==============

tg_interface
~~~~~~~~~

include in config/app.cfg::

    tg.include_widgets = ['jquery.jquery','tg_interface.tg_interface']
"""
author = "Derek Anderson"
email = "derek@enomaly.com"
copyright = "Derek Anderson 2007"

# if it's open source, you might want to specify these
url = "http://armyofevilrobots.com/"
download_url = "http://armyofevilrobots.com/tg_interface"
license = "MIT"
