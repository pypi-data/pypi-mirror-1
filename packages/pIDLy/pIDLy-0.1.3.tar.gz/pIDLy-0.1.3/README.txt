pIDLy: IDL within Python
Control ITT's IDL (Interactive Data Language) from within Python.

Version 0.1.3

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

The following are required, but should be installed automatically if you
follow the installation instructions below:
* Pexpect: http://pexpect.sourceforge.net/
* NumPy: http://numpy.scipy.org/

Also required:
* IDL: http://www.ittvis.com/idl/

Tested on 
* Mac OS X with IDL 6.4 and Python 2.5
* Linux with IDL 6.4 & 7 and Python 2.5.


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

Execute commands:
>>> idl('x = max([1, 2])')

Retrieve values:
>>> idl.x
2

Evaluate expressions:
>>> idl.ev('x ^ 2')
4

Assign value from Python expression:
>>> idl.x = 2 + 2
>>> idl.x
4

Or:
>>> idl('x', 2 + 2)
>>> idl.x
4

Perform IDL function on python expression(s)
>>> idl.reform(range(4), 2, 2)
array([[0, 1],
       [2, 3]])

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

* If an IDL error occurs, the program level does not return to $MAIN$ (retall)
* IPython: IDL hangs on exit if not closed explicitly
* IPython: prints input in interactive mode
* Slow transferring large Python arrays to IDL, e.g., 20,000 doubles in 12-15s
* Aquamacs: interactive mode has very small input buffer (253 bytes?)


6. TO DO
========

* Test on Windows
* Complex numbers
* Dictionaries/structures
* Raise exceptions (e.g., for unsupported types)
* Handle IDL errors: raise exceptions, 'retall', etc.


7. RELEASE HISTORY
==================

Version 0.1.3, 6 Feb 2008
* Added support for unsigned integers
* Fixed bug with byte/int8
* Added easy access to IDL variables and functions (__getattr__ and __setattr__)
* Various minor alterations

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
* Handles arbitrarily sized and shaped arrays of strings, ints and floats
