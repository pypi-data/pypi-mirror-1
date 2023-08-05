from setuptools import setup
setup(name='pIDLy',
      version='0.1.1',
      description='IDL within Python',
      long_description='Control ITT\'s IDL (Interactive Data Language) from within Python',
      author='Anthony Smith',
      author_email='A.J.Smith@sussex.ac.uk',
      url='http://astronomy.sussex.ac.uk/~anthonys/pidly/',
      py_modules=['pidly'],
      license='BSD',
      install_requires=['numpy', 'pexpect'],
      classifiers=['Intended Audience :: Science/Research',
                   'Programming Language :: Other',
                   'License :: OSI Approved :: BSD License']
      )
