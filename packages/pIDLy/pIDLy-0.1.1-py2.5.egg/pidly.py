"""pIDLy 0.1.1: IDL within Python.

Control ITT's IDL (Interactive Data Language) from within Python.

http://astronomy.sussex.ac.uk/~anthonys/pidly/
http://pypi.python.org/pypi/pIDLy/

Requirements:

* Pexpect
* NumPy

Usage:

>>> import pidly
>>> idl = pidly.Session()

Consult the docstrings or README.txt for further information.

Copyright (c) 2008, Anthony Smith
A.J.Smith 'at' sussex.ac.uk

"""
import sys
import re

import numpy
import pexpect

__version__ = '0.1.1'

class Session(pexpect.spawn):
    """pidly.Session() : Launch IDL session within Python.

    Methods:
    * ev : evaluate IDL expression
    * __call__ == ex : execute IDL statement or assign value to IDL variable
    * interact : make IDL shell interactive

    The Session class inherits from pexpect.spawn.  Consult pexpect
    documentation for details of further methods.

    Requirements:

    * pexpect
    * numpy

    Usage:

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

    """
    
    def __init__(self, command='idl', args=[], timeout=None, max_sendline=1024,
                 max_idl_code_area=2048):
        pexpect.spawn.__init__(self, command, args=args, timeout=timeout)
        self.expect('IDL>')
        self.max_sendline = max_sendline
        self.max_idl_code_area = max_idl_code_area


    def ev(self, expression, print_output=True):
        """Return the value of IDL expression as a numpy.ndarray."""

        # Evaluate expression and store as an IDL variable
        self.ex('delvar, pidly_tmp', print_output=print_output)
        self.ex('pidly_tmp = ' + expression, print_output=print_output)

        # Get IDL's string representation of expression
        idl_output = self.ex(
            'if n_elements(pidly_tmp) gt 0 then print, reform(pidly_tmp, '
            + 'n_elements(pidly_tmp))',
            print_output=False, ret=True)

        # Parse this string into a python variable
        if idl_output:
            idl_type = self.ex('print, size(pidly_tmp, /type)',
                               print_output=False, ret=True)
            idl_dims = self.ex('print, size(pidly_tmp, /dimensions)',
                               print_output=False, ret=True)
            return self._idl_output_to_python(idl_output, idl_type, idl_dims)


    def ex(self, expression, assignment_value=None,
           print_output=True, ret=False):
        """Execute a command in IDL.

        If assignment_value is set (to a Python expression), this value is
        assigned to the IDL variable named in expression.

        """
        
        # Assign value to expression?
        if assignment_value is not None:
            expression = self._python_to_idl_input(assignment_value,
                                                   expression)

        if hasattr(expression, '__iter__'):
            # Long assignments are broken down into lists: iterate then return
            # Or can receive a list of commands directly
            output = []
            for exp in expression:
                output.append(self.ex(exp, print_output=print_output, ret=ret))
            if ret:
                return ''.join(output)
            else:
                return

        # Send expression to IDL
        self.sendline('retall')  # Return IDL to main program level
        self.expect('IDL>')
        if len(expression) > self.max_sendline:
            if len(expression) <= self.max_idl_code_area:
                # Long line: need to send it in chunks
                for i in range((len(expression) - 1) / self.max_sendline + 1):
                    self.send(expression[self.max_sendline * i
                                         : self.max_sendline * (i + 1)])
                self.send('\n')
            else:
                print >> sys.stderr, \
                      "Expression too long for IDL to receive: cannot execute."
                print >> sys.stderr, expression
                return
        else:
            self.sendline(expression)

        # Wait for command to be completed, and optionally print output
        self.readline()  # First line of output will be IDL command
        idl_output = self._wait_for_prompt(print_output=print_output)

        # Return IDL output
        if idl_output and ret:
            return idl_output


    def interact(self, escape_character='\x04'):
        """Interactive IDL shell. Press ^D to return to Python."""
        print "IDL>",
        sys.stdout.flush()
        pexpect.spawn.interact(self, escape_character=escape_character)
    interact.__doc__ += "\n\n        " + pexpect.spawn.interact.__doc__


    # Calling the instance is the same as executing an IDL command.
    __call__ = ex

    
    # "PRIVATE" METHODS
    

    def _wait_for_prompt(self, print_output=True):
        """Read IDL output (optionally print) until IDL prompt displayed."""
        index = 1
        output_lines = []
        while index == 1:
            index = self.expect(['IDL>', '\n'])
            output_lines.append(self.before.replace('\r', ''))
            if print_output and output_lines[-1]:  # Don't print blank lines
                print output_lines[-1]
        return '\n'.join(output_lines)
        

    def _idl_output_to_python(self, idl_output, idl_type, idl_dims):
        """Take output from IDL print statement and return value."""

        # Find Python dtype and shape
        idl_type = int(idl_type)
        dtype = self._dtype_from_idl_type(idl_type)  # = None for string
        shape = self._shape_from_idl_dims(idl_dims)

        # Split the output into separate items
        value = idl_output.split()

        if value:
            if idl_type == 7:  # String
                if shape == ():
                    # Concatenate string
                    value = ' '.join(value)

            # Convert to numpy.array of appropriate type
            if dtype is None:
                value = numpy.array(value)
            else:
                value = numpy.array(value).astype(dtype)

            # Reshape array
            if numpy.product(shape) != value.size:
                print >> sys.stderr, "(!) Could not reshape array."
            elif shape:
                value = value.reshape(shape)

            if idl_type != 7 and len(value) == 1:
                return value[0]
            else:
                return value

    def _python_to_idl_input(self, python_input, assign_to):
        """Take Python value and return string suitable for IDL assignment.

        For long input, returns a list of executable strings.
        """

        if isinstance(python_input, str):
            # Strings need additional quotes
            idl_input = "\'" + python_input + "\'"

        else:
            # Convert to numpy array
            pin = numpy.array(python_input)

            if ((not isinstance(python_input, numpy.ndarray))
                and  pin.tolist() != python_input):
                print >> sys.stderr, \
                      "(!) Conversion to numpy.array has changed input from:"
                print >> sys.stderr, python_input
                print >> sys.stderr, "to:"
                print >> sys.stderr, pin.tolist()

            # String format (must have commas between elements)
            if len(pin.shape) > 1:
                # IDL can't handle list concatenations with > 3 dimensions
                str_pin = ("reform(" + str(pin.flatten().tolist()) + ", "
                           + str(pin.shape[::-1])[1:-1] + ")")
            else:
                str_pin = str(pin.tolist())

            # Cast as appropriate type
            idl_input = self._idl_cast_from_dtype(pin.dtype, str_pin)

        idl_input = assign_to + " = " + idl_input

        if len(idl_input) > self.max_idl_code_area:
            # String too long!  Need to create list of shorter commands
            idl_input = self._split_idl_assignment(pin, assign_to)

        return idl_input


    def _split_idl_assignment(self, pin, assign_to):
        """Take a very long numpy array and return a list of commands
        to execute in order to assign this value to an IDL variable."""

        idl_input = []
        extend_string = ''
        max_length = self.max_idl_code_area - 2 * len(assign_to) - 506 # ?

        # Loop until string has been split up into manageable chunks
        array_string_remaining = str(pin.flatten().tolist())[1:] # Rem '['
        while len(array_string_remaining) > max_length:
            # Maximum length string, but cut the end off to make meaningful
            cut_off_end = len(re.split(
                '.*[,\]]', array_string_remaining[:max_length])[1])

            # Create the command
            idl_input.append(assign_to + " = [" + extend_string +
                             array_string_remaining[:max_length
                                                    - cut_off_end - 1]
                             + "]")

            # Not for the first time round
            extend_string = assign_to + ", "

            # What's left?
            array_string_remaining = (
                array_string_remaining[max_length - cut_off_end + 1:])

        # Final command in assignment
        idl_input.append(assign_to + " = [" + extend_string +
                         array_string_remaining)

        if len(pin.shape) > 1:
            # Convert data type and shape
            idl_input.append(assign_to + " = " + "reform(" +
                             self._idl_cast_from_dtype(pin.dtype, assign_to)
                             + ", " + str(pin.shape[::-1])[1:-1] + ")")
        else:
            # Convert data type
            idl_input.append(assign_to + " = " +
                             self._idl_cast_from_dtype(pin.dtype, assign_to))

        return idl_input

        
    def _dtype_from_idl_type(self, idl_type):
        """Convert IDL type to numpy dtype."""

        if idl_type is not None:
            idl_type = int(idl_type)
            python_idl_types = [
                None, 'byte8', 'int16', 'int32', 'float32', 'float64',
                None, None, None, None, None,
                None, 'int32', 'int64', 'int64', 'int64']
            dtype = python_idl_types[idl_type]
            if idl_type == 12:
                print >> sys.stderr, \
                      "Warning: casting unsigned 16-bit int as 32-bit signed."
            elif idl_type == 13:
                print >> sys.stderr, \
                      "Warning: casting unsigned 32-bit int as 64-bit signed."
            elif idl_type == 15:
                print >> sys.stderr, \
                      "Warning: casting unsigned 64-bit int as 64-bit signed."
            if dtype is None and idl_type != 7:
                print >> sys.stderr, "(!) Could not convert IDL type ", \
                          + str(idl_type) + " to Python."
        else:
            dtype = None
        return dtype

    
    def _shape_from_idl_dims(self, idl_dims):
        """Convert IDL dimensions to numpy shape."""
                
        shape = []
        for dim in idl_dims.split():
            shape.append(int(dim))
        shape.reverse()  # Dimensions run the opposite way
        if shape == [0]:
            shape = []

        return tuple(shape)


    def _idl_cast_from_dtype(self, dtype, idl_str):
        """Take a NumPy dtype and return an expression to cast an IDL
        expression as appropriate type."""

        if dtype.name[0:6] == 'string':
            return idl_str
        elif dtype.name == 'int8':
            return "byte(" + idl_str + ")"
        elif dtype.name == 'int16':
            return "fix(" + idl_str + ")"
        elif dtype.name == 'int32':
            return "long(" + idl_str + ")"
        elif dtype.name == 'int64':
            return "long64(" + idl_str.replace('L', 'LL') + ")"
        elif dtype.name == 'float8':  # Not a NumPy type?
            print >> sys.stderr, "Warning: converting 8-bit to 32-bit float."
            return "float(" + idl_str + ")"
        elif dtype.name == 'float16':  # Not a NumPy type?
            print >> sys.stderr, "Warning: converting 16-bit to 32-bit float."
            return "float(" + idl_str + ")"
        elif dtype.name == 'float32':
            return "float(" + idl_str + ")"
        elif dtype.name == 'float64':
            return "double(" + idl_str + ")"
        else:
            print >> sys.stderr, "(!) Could not convert NumPy dtype", \
                  dtype.name, "to IDL."
            return

