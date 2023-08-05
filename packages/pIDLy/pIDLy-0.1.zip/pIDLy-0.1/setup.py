from distutils.core import setup
setup(name='pIDLy',
      version='0.1',
      description='IDL within Python',
      long_description='Control ITT\'s IDL (Interactive Data Language) from within Python',
      author='Anthony Smith',
      author_email='A.J.Smith@sussex.ac.uk',
      url='http://astronomy.sussex.ac.uk/~anthonys/pidly/',
      py_modules=['pidly', 'test_pidly'],
      licence='BSD',
      classifiers=['Intended Audience :: Science/Research',
                   'Programming Language :: Other',
                   'License :: OSI Approved :: BSD License']
      )
