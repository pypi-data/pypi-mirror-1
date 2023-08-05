wxOptParse
~~~~~~~~~~~

''Don't limit yourself to the command line.''

.. meta::
   :keywords: wxOptParse, optparse, wxPython, python
   :description lang=en: Graphical front end to optparse enabled python programs.

.. contents:: Table of Contents

Introduction
============

|wxoptparse| is a Python program that brings up a graphical representation of 
the options that another python program has for the command line, via the optparse_
module.

What this means is that if if you have a program that uses optparse_ you can 
click on checkboxes, edit boxes, combo boxes, etc. instead of using the command line.

So instead of this::

    usage: mytest.py [options]
    
    options:
      -h, --help            show this help message and exit
      -f FILENAME, --file=FILENAME
                            Enter a filename
      -p PATH, --path=PATH  Enter a path
      -2 FILENAME2, --noHelp=FILENAME2
      -n NUMBER, --count=NUMBER
                            Enter a number
      -m FLOAT, --float=FLOAT
                            Enter a floating point number
      -b, --bool            Switch to true
      --nbool               Switch to false
      --choice=CHOICE       Choice

You get 

.. image:: mytest-sample.png

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

* There's a sample of how you can run any program through wxOptParse, not just a python program. See wxFind.


Dependencies
============

* wxPython 2.5.3 or greater. (http://www.wxpython.org)

* elementtree 1.2 or greater (http://effbot.org/zone/element-index.htm)

* Python 2.4 (untested in 2.3). (http://www.python.org)


Download
========

http://developer.berlios.de/project/showfiles.php?group_id=4589

Installing
==========
Choose one of the following methods.  In all cases you probably need to run as root.



Egg Download
------------

::

    easy_install.py wxoptparse

Egg File
---------

::

    easy_install.py wxOptParse-0.1.2-py2.4.egg
    
Easy Install Zip
----------------
::

    easy_install.py wxOptParse-0.1.2.zip

Normal Python Install
----------------------
::

    unzip wxOptParse-0.1.2.zip
    cd wxOptParse-0.1.2
    python setup.py install
    
    

Running
=======

If you want to run your program you should be able to type:

$ wxoptparse myprogram.py



Assuming your program is called ``myprogram.py``

There's a sample program installed called wxFind which runs the GNU find command, if available. The source code shows you how it is done. Unfortunately, GNU's find doesn't use the standard style of parameters so some handling of the parameters needs to be done, but it is still quite useful.


To Do
=====

* A way to *use* your recent items (combo box) - currently it shows the lastvalue used.

* Allow you to change `your` program so that it uses, optionally, |wxOptParse|.

* A method to force an option's items type (like whether it is to browse for file/folder)

* Ability to reset the options to the defaults.

* Ability to save a set of settings and give it a name.

* Use radio buttons when appropriate.

* Use tooltips

* Run the ouput in a sub-window (I tried but wasn't able to do it).

Related Links
================

* This project's homepage http://developer.berlios.de/projects/wxoptparse/

* The Wiki is at http://openfacts.berlios.de/index-en.phtml?title=wxOptParse

* You can access via Subversion with: ::

    svn checkout svn://svn.berlios.de/wxoptparse/trunk


* ``configparse``: an optparse extension module for configuration file parsing. http://www.gustaebel.de/lars/configparse/

* My web blog: http://scottkirkwood.blogspot.com/

* My homepage (gathering cobwebs) http://forusers.com/


Changelog
=========

* Release 0.1.6 - 2006-11-13

  - Now correctly remembers last value
  - Passing commands on the command line works
  - Problems with wxpython versioning, removed.
  - The extra arguments were't saved, now they are.
  - The previous args are now saved with a dot to hide it in Linux
  - Tests were added to the package
  - Works if the .py file is in another directory
  - Tabbing in the dialog works now
  - The Go button is the default, Enter now works.

* Release 0.1.4 - 2005-10-06

  - Added sample running the find command. Added some fixes to the setup.

* Release 0.0.1 - Sept 11th, 2005

  - Initial working release.

.. _Subversion: http://subversion.tigris.org/

.. |wxoptparse| replace:: ``wxOptParse``

.. |wxOptParse| replace:: ``wxOptParse``

.. |Not supported| replace:: **- Not supported**

.. _optparse: http://www.python.org/doc/2.4/lib/module-optparse.html
