from setuptools import setup
setup(name='pIDLy',
      version='0.2.1',
      description='IDL within Python',
      long_description='Control ITT\'s IDL (Interactive Data Language) from within Python',
      author='Anthony Smith',
      author_email='A.J.Smith@sussex.ac.uk',
      url='http://astronomy.sussex.ac.uk/~anthonys/pidly/',
      py_modules=['pidly'],
      license='MIT',
      requires=['NumPy', 'Pexpect'],
      install_requires=['numpy', 'pexpect'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Science/Research',
                   'Programming Language :: Other',
                   'License :: OSI Approved :: MIT License']
      )
