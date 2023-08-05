import sys
from datetime import datetime
now = datetime.now
import time
import profile
import pstats

import numpy

import pidly

def test_pidly(do_profile=False):
    """Test pidly."""

    def t(time_delta):
        return time_delta.seconds + time_delta.microseconds / 1000000.

    def test_pidly_run():
        # Rounding error > tolerance: fail; < tolerance: warning
        tolerance = 2.01e-7
        
        passed_tests = []

        print "Testing pIDLy " + pidly.__version__ + \
              ": passing values to IDL then retrieving them."
        print "Showing (Python -> IDL time) / (IDL -> Python time).\n"

        def py_idl_py(x, desc=None):
            test_start_time = now()
            print desc, "...",
            sys.stdout.flush()
            idl.x = x
            #idl('x', x)
            test_mid_time = now()
            #y = idl.ev('x')
            y = idl.x
            npy = numpy.array(y)
            npx = numpy.array(x)
            test_end_time = now()
            try:
                if (all((npy == npx).flatten())
                    and npy.dtype.name[:6] == npx.dtype.name[:6]):
                    print "passed",
                    passed_tests.append(True)
                elif (npy.dtype.name[:6] != "string"
                      and npx.dtype.name[:6] != "string"
                      and all((abs(y - npx) < tolerance).flatten())
                      and npy.dtype.name[:6] == npx.dtype.name[:6]):
                    print "passed with rounding error",
                    print max(abs(y - npx).flatten()),
                    passed_tests.append(True)                
                else:
                    print "failed:",
                    if all((y == npx).flatten()):
                        print npx.dtype.name, "->", y.dtype.name,
                    else:
                        print "array values do not agree!",
                    passed_tests.append(False)
            except TypeError:  # Dictionary
                if hasattr(npx.tolist(), 'keys'):
                    npx = numpy.array([npx])
                    npy = numpy.array([npy])
                passed = True
                rounding_error = 0
                for i, npxi in enumerate(npx):  # For each dictionary in list
                    npxi = numpy.array(npxi)
                    npyi = numpy.array(npy[i])
                    if not passed:
                        break
                    for key in npxi.tolist():
                        xk = numpy.array(npxi.tolist()[key])
                        yk = numpy.array(npyi.tolist()[key])
                        if (all((xk == yk).flatten())
                            and (xk.dtype.name[:6] == yk.dtype.name[:6])):
                            continue
                        elif (xk.dtype.name[:6] != "string"
                              and yk.dtype.name[:6] != "string"
                              and all((abs(yk - xk) < tolerance).flatten())
                              and (xk.dtype.name[:6] == yk.dtype.name[:6])):
                            rounding_error = max(rounding_error,
                                                 max(abs(yk - xk).flatten()))
                        else:
                            passed = False
                            print "failed:",
                            if all((yk == xk).flatten()):
                                print xk.dtype.name, "->", yk.dtype.name,
                            else:
                                print "array values do not agree!",
                                print xk, yk
                            break
                if passed:
                    print "passed",
                    if rounding_error:
                        print "with rounding error", rounding_error,
                passed_tests.append(passed)
            print "in %0.5ss/%0.5ss" % (t(test_mid_time - test_start_time),
                                        t(test_end_time - test_mid_time))

        tests = [
            (2, "Single integer"),
            (2.123, "Single float"),
            ('hello', "Single string"),
            ('hello there', "multi-word string"),
            ([' 5 2  5k 2', '4  33 55 1 ', ' 4 ', '2', '  3   2'],
             "String array"),
            (25525252525525, "Long integer"),
            ([1,2,4,2555], "Array of ints"),
            ([1,2,3,25525252525525,23, 5, 6, 5, 2, 5, 7, 8, 3, 5],
             "Arr long int"),
            ([[1,2,3],[3,4,5]], "2D int arr"),
            ([[[ 1, 2, 3],[ 4, 5, 6]],[[ 7, 8, 9],[10,11,12]],
                 [[13,14,15],[16,17,18]],[[19,20,21],[22,23,24]]],
             "3D int arr"),
            ([22,23.,'24'], "Mixed arr (warning message coming)\n"),
            (dict(a=2), "Simple dictionary"),
            ({'a':'ah', 'b':1e7, 'c':0.7}, "3-element dict"),
            ([{'a':'ah', 'b':1000L, 'c':0.7}, {'a':'be', 'b':8L, 'c':-6.3},
              {'a':'x', 'b':0L, 'c':81.}], "3 3-dicts"),
            ([{'a':numpy.random.random(2),
               'b':(numpy.random.random(1)*100).astype('string')}
              for i in range(100)], "100 dicts"),
            (numpy.arange(2*3*4*5).reshape(2,3,4,5), "4D int arr"),
            (numpy.arange(2*3*4*5*6*7).reshape(2,3,4,5,6,7), "6D int arr"),
            (numpy.arange(2*3*1*1*4*5*6*7).reshape(2,3,1,1,4,5,6,7),
             "8D int arr"),
            (numpy.random.random(50), "50 doubles"),            
            (numpy.random.random(20000), "20000 doubles"),
            ]

        # Run tests

        # Launch IDL
        idl = pidly.IDL()

        # Start timer
        start_time = now()

        # Run tests
        print "idl.reform(range(4), 2, 2) ...",
        sys.stdout.flush()
        if (idl.reform(range(4), 2, 2).tolist()
            == numpy.array([[0, 1], [2, 3]]).tolist()):
            print "passed"
        else:
            print "failed"

        print "Sending longest line ...",
        sys.stdout.flush()
        x = ["x='"]
        for i in range(idl.max_sendline - 4):
            x.append('a')
        x.append("'")
        s = ''.join(x)
        test_start_time = now()
        idl.sendline(s)
        idl.expect('IDL> ')
        print "done in %0.5ss" % t(now() - test_start_time)

        print "Sending longest string ...",
        sys.stdout.flush()
        x = ["x='"]
        for i in range(idl.max_idl_code_area - 4):
            x.append('a')
        x.append("'")
        s = ''.join(x)
        test_start_time = now()
        idl(s)
        print "done in %0.5ss" % t(now() - test_start_time)

        for x, desc in tests:
            py_idl_py(x, desc)

        print "5000 doubles, one at a time ...",
        sys.stdout.flush()
        n = 5000
        x = numpy.random.random(n)
        test_start_time = now()
        idl('x = dblarr(' + str(n) + ')')
        for i in range(n):
            idl('x[' + str(i) + ']', x[i])
            if (i + 1) % 100 == 0:
                print (i + 1),
                sys.stdout.flush()
        test_mid_time = now()
        y = idl.ev('x')
        test_end_time = now()
        if all(abs(y - numpy.array(x)) < tolerance):
            print "passed with rounding error",
            print max(abs(y - numpy.array(x))),
        else:
            print "failed",
        print "in %0.5ss/%0.5ss" % (t(test_mid_time - test_start_time),
                                    t(test_end_time - test_mid_time))
        
        # End
        if all(passed_tests):
            print "\nPassed!"
        else:
            print "\nNot all tests passed! Failed:"
            for i, test in enumerate(tests):
                if passed_tests[i] == False:
                    print "\t", test[1]
                    
        print "Total time,", now() - start_time, "seconds."

        idl.close()


    if do_profile:
        p = profile.Profile()
        p.runctx("test_pidly_run()", globals(), locals())
        s = pstats.Stats(p)
        s.sort_stats("time", "name").print_stats()
    else:
        test_pidly_run()

if __name__ == "__main__":
    test_pidly()
