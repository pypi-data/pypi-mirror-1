"""pIDLy 0.2.2: IDL within Python.

Control ITT's IDL (Interactive Data Language) from within Python.

http://astronomy.sussex.ac.uk/~anthonys/pidly/
http://pypi.python.org/pypi/pIDLy/

Requirements:

* Pexpect
* NumPy

Usage:

>>> import pidly
>>> idl = pidly.IDL()

>>> print idl.__doc__

Consult the docstrings or README.txt in the source distribution for
further information.

Copyright (c) 2008, Anthony Smith
A.J.Smith 'at' sussex.ac.uk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
import sys
import re

import numpy
import pexpect


__version__ = '0.2.2'
STR_DELIMITER = '!@#'  # To distinguish items in an array of strings

try:  # If module is reloaded when IDL is active: close IDL
    for pidly_session in pidly_open_sessions[:]:
        pidly_session.close()
except NameError:
    pass

# For clean exit with IPython
# Rewrite IPython exit so IDL doesn't run wild when IPython exits
# Do so by explicitly closing pIDLy sessions before exiting IPython
try:
    def pidly_exit():
        # From IPython exit method
        if __IPYTHON__.rc.confirm_exit:
            if __IPYTHON__.ask_yes_no(
                'Do you really want to exit ([y]/n)?','y'):
                for pidly_session in pidly_open_sessions[:]:
                    pidly_session.close()
                __IPYTHON__.exit_now = True
        else:
            for pidly_session in pidly_open_sessions[:]:
                pidly_session.close()
            __IPYTHON__.exit_now = True
    __IPYTHON__.exit = pidly_exit
    pidly_open_sessions = []
    ipython = True
except NameError:
    ipython = False


def close_all():
    for pidly_session in pidly_open_sessions:
        pidly_session.close()


class IDL(pexpect.spawn):
    """pidly.IDL() : Launch IDL session within Python.

    The IDL class inherits from pexpect.spawn.  Consult pexpect
    documentation for details of further methods.

    Usage:

    Initiate:
    >>> import pidly
    >>> idl = pidly.IDL()

    Or:
    >>> idl = pidly.IDL('/path/to/idl')

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

    With keywords (/L64 -> L64=True or L64=1)
    >>> idl.histogram(range(4), binsize=3, L64=True)
    array([3, 1], dtype=int64)

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
    * dictionaries <-> structures & lists of dicts <-> arrays of structures
      but with certain limitations on transfer from Python to IDL

    [NB if getting Syntax Errors when passing large arrays to IDL, try using
    >>> idl = pidly.IDL(long_delay=0.05)
    default is 0.02.]

    """

    def __init__(self, *arguments, **kwargs):
        # The speed Py -> IDL is limited by the IDL input buffer,
        # which can overload.  self.delaybeforesend is increased
        # before sending long arrays.
        self.short_delay = kwargs.pop('short_delay', 0)
        # As small as possible! (try 0.014)
        self.long_delay = kwargs.pop('long_delay', 0.02)

        # There are limits to how data may be passed to IDL:
        # max_sendline is the number of bytes that may be sent in one line
        # (Final, additional, byte is the end-of-line)
        self.max_sendline = kwargs.pop('max_sendline', 1023)

        # max_idl_code_area is the maximum number of bytes that may
        # be input as an IDL command. This limit may be reached by
        # splitting the line and sending as more than one send()
        # command
        self.max_idl_code_area = kwargs.pop('max_idl_code_area', 2048)

        # Number of array elements in IDL code area limited to 331 (don't ask)
        self.max_n_elements_code_area = kwargs.pop('max_n_elements_code_area',
                                                   331)

        # Custom IDL prompt
        self.idl_prompt = kwargs.pop('idl_prompt', 'IDL> ')
        
        # Begin
        if len(arguments) == 0:
            arguments = ('idl',)
        if not kwargs.has_key('timeout'):
            kwargs['timeout'] = None
        pexpect.spawn.__init__(self, *arguments, **kwargs)
        self.delaybeforesend = self.short_delay  # Changed for long commands
        self._wait_for_prompt()

        # For clean exit in IPython
        if ipython:
            pidly_open_sessions.append(self)
            i = 0
            while i < len(pidly_open_sessions):  # Garbage collection
                # 1 ref in list, 1 temporarily in getrefcount
                if sys.getrefcount(pidly_open_sessions[i]) <= 2:
                    pidly_open_sessions[i].close()
                else:
                    i = i + 1

        self.ready = True  # For __setattr__


    def ex(self, expression, assignment_value=None,
           print_output=True, ret=False):
        """Execute a command in IDL.

        If assignment_value is set (to a Python expression), this value is
        assigned to the IDL variable named in expression.

        """
        
        # Assign value to expression?
        if assignment_value is not None:
            expression = self._python_to_idl_input(assignment_value, expression)

        # List of commands to execute?
        if hasattr(expression, '__iter__'):
            # Long assignments are broken down into lists: iterate then return
            # Or can receive a list of commands directly
            output = []
            for exp in expression:
                out = self.ex(exp, print_output=print_output, ret=ret)
                if out:
                    output.append(out)
                self.delaybeforesend = self.long_delay
            self.delaybeforesend = self.short_delay
            if ret:
                return ''.join(output)
            else:
                return

        # Send expression to IDL
        if self._send_expression_to_idl(expression):  # Any bytes sent?
            # Wait for command to be completed, and optionally print output
            self.readline()  # First line of output will be IDL command repeated
            idl_output = self._wait_for_prompt(print_output=print_output)

            # Return IDL output
            if ret and idl_output:
                return idl_output


    def ev(self, expression, print_output=True):
        """Return the value of an IDL expression as a numpy.ndarray."""

        # Evaluate expression and store as an IDL variable
        self.ex('pidly_tmp=' + expression, print_output=print_output)

        # Get IDL's string representation of expression
        # Special treatment of arrays of type string (type == 7)
        idl_output = self.ex(
            'if size(pidly_tmp,/type) eq 7 and n_elements(pidly_tmp) gt 1 '
            + 'then print,strjoin(pidly_tmp,\'' + STR_DELIMITER + '\') '
            + 'else if n_elements(pidly_tmp) gt 0 then print,reform(pidly_tmp,'
            + 'n_elements(pidly_tmp))',
            print_output=False, ret=True)

        # Parse this string into a python variable
        if idl_output:
            # These two could be combined
            idl_type = self.ex('print,size(pidly_tmp,/type)',
                               print_output=False, ret=True)
            idl_dims = self.ex('print,size(pidly_tmp,/dimensions)',
                               print_output=False, ret=True)
            if int(idl_type) == 8:  # Structure
                self.ex('help,pidly_tmp,/struct,output=pidly_tmp_2',
                        print_output=False)
                idl_struct = self.ev('pidly_tmp_2').tolist()
                return self._idl_struct_to_python(idl_output, idl_struct)
            else:
                return self._idl_output_to_python(idl_output, idl_type,
                                                  idl_dims)


    def interact(self, **kwargs):
        """Interactive IDL shell. Press ^D to return to Python."""

        print self.idl_prompt,
        sys.stdout.flush()
        if not kwargs.has_key('escape_character'):
            kwargs['escape_character'] = '\x04'
        pexpect.spawn.interact(self, **kwargs)
    interact.__doc__ += "\n\n        " + pexpect.spawn.interact.__doc__


    def variables(self):
        """Return list of names of defined IDL variables."""

        # Retrieve output from IDL help command ('help' without 'output=...'
        # prints one screen at a time, waiting for spacebar...)
        self.ex('help, output=pidly_tmp')
        help_output = self.ev('pidly_tmp').tolist()  # String array
        variable_list = []
        for line in help_output[1:]:  # 1st line = "%..."
            if line.startswith('Compiled'):  # End of variable list
                break
            elif line and not line.startswith('%'):
                variable_list.append(line.split()[0])
        return variable_list


    def close(self):
        pexpect.spawn.close(self)
        # Remove additional reference to this object
        if ipython:
            try:
                pidly_open_sessions.remove(self)
            except ValueError:
                pass
    close.__doc__ = pexpect.spawn.close.__doc__


    # Special methods


    # Calling the instance is the same as executing an IDL command.
    __call__ = ex


    def __getattr__(self, name):
        """Get IDL attribute.

        idl.x: return the value of 'x' from IDL.
        idl.f(x,y,...): return the value of IDL f() of Python variables x,y,...
        
        """

        # idl.x
        if name.upper() in self.variables():
            return self.ev(name)

        # idl.f(x,y,...)
        elif (not name.startswith('_')
              and name not in ['trait_names', 'pidly_tmp']):  # for IPython
            def idl_function(*args, **kwargs):
                string_bits = []
                for arg in args:
                    string_bits.append(self._python_to_idl_input(arg))
                for kwarg in kwargs:
                    string_bits.append(
                        kwarg + '=' + self._python_to_idl_input(kwargs[kwarg]))
                return self.ev(name + '(' + ','.join(string_bits) + ')')
            return idl_function


    def __setattr__(self, name, value):
        """Set IDL attribute: idl.x = ..."""

        if self.__dict__.has_key('ready'):
            # __init__ has finished
            if self.__dict__.has_key(name):
                pexpect.spawn.__setattr__(self, name, value)
            else:
                self.ex(name, value)
        else:
            # __init__ in progress
            pexpect.spawn.__setattr__(self, name, value)


    # "PRIVATE" METHODS


    # Sending to IDL
    

    def _send_expression_to_idl(self, expression):
        # retall in case error has occurred in IDL, but takes time!
##        self.sendline('retall')  # Return IDL to main program level
##        self.expect('IDL>')
        if len(expression) > self.max_sendline:
            if len(expression) <= self.max_idl_code_area:
                # Long line: need to send it in chunks
                expression = ''.join([expression, '\n'])
                for i in range((len(expression) - 1)
                               / (self.max_sendline + 1) + 1):
                    self.send(expression[(self.max_sendline + 1) * i
                                         : (self.max_sendline + 1) * (i + 1)])
                    self.delaybeforesend = self.long_delay
                self.delaybeforesend = self.short_delay
                return True
            else:
                print >> sys.stderr, \
                      "Expression too long for IDL to receive: cannot execute"
                print >> sys.stderr, expression
                return False
        else:
            return self.sendline(expression)


    def _python_to_idl_input(self, python_input, assign_to=None):
        """Take Python value and return string suitable for IDL assignment.

        For long input, returns a list of executable strings.
        """

        if assign_to is not None:
            assign_to_str = assign_to + "="
        else:
            assign_to_str = ''

        if isinstance(python_input, str):
            # Strings need additional quotes
            idl_input = assign_to_str + "\'" + python_input + "\'"

        else:
            # Convert to numpy array
            py_in = numpy.array(python_input)

            # Display warning if conversion has changed the array values
            if ((not isinstance(python_input, numpy.ndarray))
                and  py_in.tolist() != python_input):
                print >> sys.stderr, \
                    "(!) Conversion to numpy.array has changed input from:"
                print >> sys.stderr, python_input
                print >> sys.stderr, "to:"
                print >> sys.stderr, py_in.tolist()

            # String format (must have commas between elements)
            str_py_in = str(py_in.flatten().tolist()).replace(' ', '')
            if len(py_in.shape) > 1:
                # IDL can't handle list concatenations with > 3 dimensions
                str_py_in_shape = ("reform(" + str_py_in + ","
                                   + str(py_in.shape[::-1])[1:-1] + ")")
            else:
                str_py_in_shape = str(py_in.tolist())
            
            # Dictionary?  Convert to IDL structure
            if ((not hasattr(python_input, 'keys')
                 and hasattr(python_input, '__iter__')
                 and hasattr(python_input[0], 'keys'))
                or hasattr(python_input, 'keys')):
                return self._python_to_idl_structure(python_input, assign_to)
            else:
                # Cast as appropriate type
                idl_input = self._idl_cast_from_dtype(py_in.dtype,
                                                      str_py_in_shape)

            idl_input = ''.join([assign_to_str, idl_input])

            if (len(idl_input) > self.max_idl_code_area
                or len(py_in.flatten()) > self.max_n_elements_code_area):
                # String too long!  Need to create list of shorter commands
                idl_input = self._split_idl_assignment(py_in, str_py_in,
                                                       assign_to)

        return idl_input


    def _split_idl_assignment(self, py_in, str_py_in, assign_to):
        """Take a very long numpy array and return a list of commands
        to execute in order to assign this value to an IDL variable."""

        if assign_to is None:
            print >>stderr, "(!) No assign_to set."

        idl_input = []
        extend_string = ''

        # Each assignment string must be no longer than max_idl_code_area:
        #      assign_to=[assign_to,<max_length>
        max_length = self.max_idl_code_area - 2 * len(assign_to) - 3

        # In addition, code area limited by number of elements of array
        max_n_elements = self.max_n_elements_code_area

        # Loop until string has been split up into manageable chunks
        array_string_remaining = str_py_in[1:]  # Remove '['
        while len(array_string_remaining) > 1:
            # Take the first max_n_elements elements (separated by
            # commas) of the first max_length characters of the string
            max_string = re.match('([^,]*[,\]]){,' + str(max_n_elements) + '}',
                                  array_string_remaining[:max_length]).group()

            # Remove final character (',' or ']') from max_string
            idl_input.append(assign_to + "=[" + extend_string +
                             max_string[:-1] + "]")

            # Not for the first time round
            extend_string = ''.join([assign_to, ","])

            # What's left?
            array_string_remaining = array_string_remaining[len(max_string):]

        if len(py_in.shape) > 1:
            # Convert data type and shape
            idl_input.append(assign_to + "=" + "reform(" +
                             self._idl_cast_from_dtype(py_in.dtype, assign_to)
                             + ", " + str(py_in.shape[::-1])[1:-1] + ")")
        else:
            # Convert data type
            idl_input.append(assign_to + "=" +
                             self._idl_cast_from_dtype(py_in.dtype, assign_to))

        return idl_input

        
    def _idl_cast_from_dtype(self, dtype, idl_str):
        """Take a NumPy dtype and return an expression to cast an IDL
        expression as appropriate type."""

        if dtype.name[0:6] == 'string':
            return idl_str
        elif dtype.name == 'bool':
            return "byte(" + str(int(eval(idl_str))) + ")"
        elif dtype.name == 'uint8':
            return "byte(" + idl_str + ")"
        elif dtype.name == 'int16':
            return "fix(" + idl_str + ")"
        elif dtype.name == 'uint16':
            return "uint(" + idl_str + ")"
        elif dtype.name == 'int32':
            return "long(" + idl_str + ")"
        elif dtype.name == 'uint32':
            return "ulong(" + idl_str + ")"
        elif dtype.name == 'int64':
            return "long64(" + idl_str.replace('L', 'LL') + ")"
        elif dtype.name == 'uint64':
            return "ulong64(" + idl_str.replace('L', 'LL') + ")"
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


    def _python_to_idl_structure(self, py_in, assign_to):
        """Given a Python dictionary, or a (simple, 1D) list of dictionaries,
        return list of commands to assign IDL structure to assign_to."""

        if hasattr(py_in, 'keys'):
            n_rows = 1
            py_in_row = py_in
        else:  # List of dictionaries
            n_rows = len(py_in)
            py_in_row = py_in[0]
            
        # Make one row
        struct_fields = []
        for key in py_in_row:
            struct_fields.append(''.join(
                [key, ':', self._python_to_idl_input(py_in_row[key])]))

        # Commands to execute
        idl_input = [assign_to + '={' + ','.join(struct_fields) + '}']
            
        if n_rows > 1:
            # Fill rows with data
            for row in py_in[1:]:
                struct_fields = []
                for key in row:
                    struct_fields.append(''.join(
                        [key, ':', self._python_to_idl_input(row[key])]))
                idl_input.append(assign_to + '=[' + assign_to + ',{'
                                     + ','.join(struct_fields) + '}]')

        return idl_input
        

    # Receiving from IDL


    def _wait_for_prompt(self, print_output=False):
        """Read IDL output until IDL prompt displayed and return."""
        index = 1
        output_lines = []
        while index == 1:
            index = self.expect([self.idl_prompt, '\n'])
            new_line = self.before.replace('\r', '')
            if new_line:
                output_lines.append(new_line)
                if print_output:
                    print new_line  # Live output while waiting for prompt
        return '\n'.join(output_lines)
        

    def _idl_output_to_python(self, idl_output, idl_type, idl_dims):
        """Take output from IDL print statement and return value."""

        # Find Python dtype and shape
        idl_type = int(idl_type)
        dtype = self._dtype_from_idl_type(idl_type)  # = None for string
        shape = self._shape_from_idl_dims(idl_dims)
            
        # Split the output into separate items
        if idl_type == 7:
            value = idl_output.split(STR_DELIMITER)
        else:
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


    def _dtype_from_idl_type(self, idl_type):
        """Convert IDL type to numpy dtype."""

        if idl_type is not None:
            idl_type = int(idl_type)
            python_idl_types = [
                None, 'uint8', 'int16', 'int32', 'float32', 'float64',
                None, None, None, None, None,
                None, 'uint16', 'uint32', 'int64', 'uint64']
            dtype = python_idl_types[idl_type]
            if dtype is None and idl_type != 7:
                print >> sys.stderr, "(!) Could not convert IDL type " \
                      + str(idl_type) + " to Python."
        else:
            dtype = None
        return dtype

    
    def _shape_from_idl_dims(self, idl_dims):
        """Convert IDL dimensions to numpy shape."""
                
        shape = []
        for dim in idl_dims.split():
            shape.append(int(dim))
        shape.reverse()  # Dimensions run the opposite way, Python vs IDL
        if shape == [0]:
            shape = []

        return tuple(shape)


    def _idl_struct_to_python(self, idl_output, idl_struct):
        """Take print output of IDL structure and return Python dictionary.

        No spaces allowed in field names, types or values.

        """

        # Create meta-dictionary
        dict_def = []
        j = 1  # Omit first line
        for i in range(1, int(idl_struct[0].split()[3]) + 1):  # Number of tags
            # For each field, store (name, dtype, shape) in the meta-dictionary
            name = idl_struct[j].split()[0]
            try:
                idl_type = self._idl_type_from_name(idl_struct[j].split()[1])
                idl_dims = self._dims_from_struct_help(idl_struct[j].split()[2])
            except IndexError:  # Some descriptions span two lines
                j += 1
                idl_type = self._idl_type_from_name(idl_struct[j].split()[0])
                idl_dims = self._dims_from_struct_help(idl_struct[j].split()[1])
            dict_def.append((name, idl_type, idl_dims))
            j += 1
                
        dict_list = []
        rows = idl_output[1:-1].split('}{')  # Remove { and } at ends
        for row in rows:
            # Create a dictionary for each row
            items = row.split()
            dict_row = {}
            for name, idl_type, idl_dims in dict_def:
                idl_out_list = []
                for i in range(numpy.product(numpy.array(
                    idl_dims.split()).astype(int))):  # Number of values
                    idl_out_list.append(items.pop(0))
                idl_out = ' '.join(idl_out_list)
                dict_row[name.lower()] = self._idl_output_to_python(
                    idl_out, idl_type, idl_dims)
            dict_list.append(dict_row)

        if len(dict_list) == 1:
            return dict_list[0]
        else:
            return dict_list


    def _idl_type_from_name(self, type):
        """Return IDL type code, given type name."""

        if type == 'BYTE':
            return '1'
        elif type == 'INT':
            return '2'
        elif type == 'LONG':
            return '3'
        elif type == 'FLOAT':
            return '4'
        elif type == 'DOUBLE':
            return '5'
        elif type == 'COMPLEX':
            return '6'
        elif type == 'STRING':
            return '7'
        elif type == 'STRUCT':
            return '8'
        elif type == 'DCOMPLEX':
            return '9'
        elif type == 'POINTER':
            return '10'
        elif type == 'OBJREF':
            return '11'
        elif type == 'UINT':
            return '12'
        elif type == 'ULONG':
            return '13'
        elif type == 'LONG64':
            return '14'
        elif type == 'ULONG64':
            return '15'


    def _dims_from_struct_help(self, struct_help):
        """Return IDL dims given description from structure."""

        try:
            dims = re.search('(?<=Array\[).*\]', struct_help).group()[:-1]
            idl_dims = dims.replace(',', ' ')
            return idl_dims
        except AttributeError:
            return '1'
