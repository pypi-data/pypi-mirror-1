import sys
import time
import profile
import pstats

import numpy

import pidly

def test_pidly(do_profile=False):
    """Test pidly."""

    def test_pidly_run():
        start_time = time.time()

        # Launch IDL
        idl = pidly.Session(timeout=300)

        passed_tests = []

        # 1. Pass integer to IDL and retrieve it
        x = 2
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(y.tolist() == x
                            and y.dtype == numpy.array(x).dtype)
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '.',
        sys.stdout.flush()

        # 2. Pass float to IDL and retrieve it
        x = 2.123
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(abs(y.tolist() - x) < 0.00001
                            and y.dtype == numpy.array(x).dtype)
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 3. Pass string (no spaces) to IDL and retrieve it
        x = 'hello'
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(
            y.tolist() == x
            and y.dtype.name[:6] == numpy.array(x).dtype.name[:6])
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 4. Pass multi-word string to IDL and retrive it
        x = 'hello there'
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(
            y.tolist() == x
            and y.dtype.name[:6] == numpy.array(x).dtype.name[:6])
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 5. Pass a very long integer to IDL and retrieve it
        x = 25525252525525
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(y.tolist() == x
                            and y.dtype == numpy.array(x).dtype)
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 6. Pass array of integers to IDL and retrieve it
        x = [1,2,4,2555]
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(y.tolist() == x
                            and y.dtype == numpy.array(x).dtype)
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 7. Pass a long 1-d array to IDL and retrieve it
        x = [1,2,3,25525252525525,23, 5, 6, 5, 2, 5, 7, 8, 3, 5]
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(y.tolist() == x
                            and y.dtype == numpy.array(x).dtype)
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 8. Pass a 2-d array to IDL and retrieve it
        x = [[1,2,3],[3,4,5]]
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(y.tolist() == x
                            and y.dtype == numpy.array(x).dtype)
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 9. Pass a 3-d array to IDL and retrieve it
        x = [[[ 1, 2, 3],[ 4, 5, 6]],[[ 7, 8, 9],[10,11,12]],
             [[13,14,15],[16,17,18]],[[19,20,21],[22,23,24]]]
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(y.tolist() == x
                            and y.dtype == numpy.array(x).dtype)
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 10. Pass a 3-d array mixed floats, strings, ints and retrieve it
        x = [[[ 1, 2, 3],[ 4, 5, 6]],[[ 7, 8, 9],[10,11,12]],
             [[13,14,15],[16,17,18]],[[19,20,21],[22,23.,'24']]]
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(
            y.tolist() == numpy.array(x).tolist()
            and y.dtype.name[:6] == numpy.array(x).dtype.name[:6])
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 11. Pass a 4-d array to IDL and retrieve it
        x = numpy.arange(2*3*4*5).reshape(2,3,4,5)
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(y.tolist() == x.tolist()
                            and y.dtype == numpy.array(x).dtype)
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 12. Pass a 6-d array to IDL and retrieve it
        x = numpy.arange(2*3*4*5*6*7).reshape(2,3,4,5,6,7) # Too long!
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(y.tolist() == x.tolist()
                            and y.dtype == numpy.array(x).dtype)
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 13. Pass an 8-d array to IDL and retrieve it (with trailing dims)
        x = numpy.arange(2*3*1*1*4*5*6*7).reshape(2,3,1,1,4,5,6,7)
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(y.tolist() == x.tolist()
                            and y.dtype == numpy.array(x).dtype)
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 14. Pass a long 1-d array of doubles to IDL and retrieve it
        x = numpy.arange(20000, dtype='float64')
        idl('x', x)
        y = idl.ev('x')
        passed_tests.append(y.tolist() == x.tolist()
                            and y.dtype == numpy.array(x).dtype)
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        # 15. Pass a literal integer to IDL and retrieve it
        x = 23
        idl('x', 23)
        y = idl.ev('x')
        passed_tests.append(y.tolist() == x
                            and y.dtype == numpy.array(x).dtype)
        if passed_tests[-1] == False:
            print 'Failed test', len(passed_tests),
        print '\b.',
        sys.stdout.flush()

        print passed_tests
        passed_tests = numpy.array(passed_tests)
        if passed_tests.all():
            print "Passed!"
        else:
            print "Not all tests passed! Failed:"
            print 1 + numpy.arange(len(passed_tests))[passed_tests == False]

        print "in", time.time() - start_time, "seconds."


    if do_profile:
        p = profile.Profile()
        p.runctx("test_pidly_run()", globals(), locals())
        s = pstats.Stats(p)
        s.sort_stats("time", "name").print_stats()
    else:
        test_pidly_run()

if __name__ == "__main__":
    test_pidly()
