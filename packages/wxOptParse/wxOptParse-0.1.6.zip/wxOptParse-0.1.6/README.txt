Introduction
============

wxOptparse is a Python program that brings up a graphical representation of 
the options that another python program has for the command line, via the optparse
module.

What this means is that if if you have a program that uses optparse you can 
click on checkboxes, edit boxes, combo boxes, etc. instead of using the command line.

Features
========

* Cross-platform.  Should work on Windows, Linux, Unix, or Mac.

* Absolutely no changes required for the program you want to run.

* You can continue to use the program at the command line as well.

* Boolean flags shown as checkboxes.

* String options that use the word "file" add a file browser button.

* String options that use the work "path" or "folder" add a path browser button.

* Choices are shown as a combo box.

* Your most recently used choices are used by default.

* A history of your previous items are stored.


Dependencies
============

* wxPython 2.5.3 or greater. (http://www.wxpython.org)

* elementtree 1.2 or greater (http://effbot.org/zone/element-index.htm)

* Python 2.4 (untested in 2.3). (http://www.python.org)

Download
========


Installing
==========
Choose one of the following methods.  In all cases you probably need to run as root.


Egg Download
------------

    # easy_install.py wxoptparse

Egg File
---------

    # easy_install.py wxOptParse-x.y.z-py2.4.egg
    
Easy Install Zip
----------------

    # easy_install.py wxOptParse-x.y.z.zip

Normal Python Install
----------------------

    # unzip wxOptParse-x.y.z.zip
    # cd wxOptParse-x.y.z
    # python setup.py install
    

Running
=======

If you want to run your program you should be able to type:

    $ wxoptparse myprogram.py


Under Windows you may need to add "c:\Python2.4\scripts" to your path 
(or whatever directory python is installed)
in order to run wxoptparse.  
The standard Python installer does not appear to do this for you.

