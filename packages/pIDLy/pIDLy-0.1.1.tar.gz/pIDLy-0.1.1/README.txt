pIDLy: IDL within Python
Control ITT's IDL (Interactive Data Language) from within Python.

Version 0.1.1

Copyright (c) 2008, Anthony Smith
A.J.Smith 'at' sussex.ac.uk


CONTENTS
========

1. Requirements
2. Installation
3. Usage
4. Further information
5. Known bugs/issues
6. To do
7. Release history


1. REQUIREMENTS
===============

The following are required, but will be installed automatically if you
follow the installation instructions below:
* Pexpect: http://pexpect.sourceforge.net/
* NumPy: http://numpy.scipy.org/

Also required:
* IDL: http://www.ittvis.com/idl/

Tested on Mac and Linux platforms with IDL 6.4 and Python 2.5.


2. INSTALLATION
===============

1. Type "easy_install pidly"

If that fails:

1. Download http://peak.telecommunity.com/dist/ez_setup.py and run it
(type "python ez_setup.py")
2. Type "easy_install pidly"


3. USAGE
========

Initiate:
>>> import pidly
>>> idl = pidly.Session()

Execute commands or evaluate expressions:
>>> idl('x = 1 + 1')
>>> idl.ev('x')
2

Assign value from Python expression:
>>> idl('x', 2 + 2)
>>> idl.ev('x')
4

Interactive mode:
>>> idl.interact()
IDL> print, x
     4
IDL> ^D
>>>

Close:
>>> idl.close() 


4. FURTHER INFORMATION
======================

Available on the pIDLy web page:
  http://astronomy.sussex.ac.uk/~anthonys/pidly/
or from the Python Package Index:
  http://pypi.python.org/pypi/pIDLy/
or from the author:
  A.J.Smith 'at' sussex.ac.uk


5. KNOWN BUGS/ISSUES
====================

* iPython: hangs on exit if not closed explicitly
* iPython: prints input in interactive mode


6. TO DO
========

* Test on Windows
* Complex numbers
* Dictionaries/structures
* Passing of arguments in wrapper methods
* Limit to amount of data that can be passed at once: not well understood
* Raise exceptions (e.g., for unsupported types)


7. RELEASE HISTORY
==================

Version 0.1.1, 1 Feb 2008
* Removed timeout limit
* Fixed typo in licence
* README and LICENCE files
* Various minor alterations

Version 0.1, 31 Jan 2008
* Wrapper on Pexpect, with conversions between IDL data and NumPy arrays
* Handles arbitrarily size and shaped arrays of strings, ints and floats
