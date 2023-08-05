pIDLy: IDL within Python
Control ITT's IDL (Interactive Data Language) from within Python.

Version 0.1.2

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
>>> idl = pidly.IDL()

[NB if getting Syntax Errors when passing large arrays to IDL, try using
>>> idl = pidly.IDL(long_delay=0.05)
default is 0.02.]

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

pIDLy supports the transfer of:
* ints
* floats
* strings
* arrays of the above types, with arbitrary size and shape


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

* iPython: IDL hangs on exit if not closed explicitly
* iPython: prints input in interactive mode
* Slow transferring large Python arrays to IDL, e.g., 20,000 doubles in 12-15s
* Mac only: interactive mode has very small input buffer (253 bytes?)


6. TO DO
========

* Test on Windows
* Complex numbers
* Dictionaries/structures
* Passing of arguments in wrapper methods
* Raise exceptions (e.g., for unsupported types)
* Handle IDL errors


7. RELEASE HISTORY
==================

Version 0.1.2, 4 Feb 2008
* Performance improvement:
  * 5-100 times faster, tranferring from Python to IDL
  * ~1.5x faster, transferring from IDL to Python
* Renamed Session class to IDL
* Various minor alterations

Version 0.1.1, 1 Feb 2008
* Removed timeout limit
* Fixed typo in license
* README and LICENSE files
* Various minor alterations

Version 0.1, 31 Jan 2008
* Wrapper on Pexpect, with conversions between IDL data and NumPy arrays
* Handles arbitrarily size and shaped arrays of strings, ints and floats
