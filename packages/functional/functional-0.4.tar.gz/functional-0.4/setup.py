try:
	from setuptools import setup
except:
	from distutils.core import setup

setup(
    name = 'functional',
    version = '0.4',
    description = "Tools for functional programming in python",
    
    long_description = """functional provides a pure-Python implementation of numerous tools common in
functional programming, such as foldl, foldr, take, flip, as well as mechanisms
for partial function application and function composition.

In addition, this project serves as a test-bed for the functional module that
will be shipped with Python 2.5. While the module to be shipped with Python will
be partially written in C for speed, this module is written in Python to gain
readability and portability.

functional currently offers over 20 tools to make functional programming a snap.
Also included is an examples.py file to provide some demo code for the tools
available in functional.""",
	
    author = 'Collin Winter',
    author_email = 'collinw@gmail.com',
    url = 'http://oakwinter.com/code/functional/',
    license = 'MIT License',
    classifiers = [    	
    	'Intended Audience :: Developers',
    	'License :: OSI Approved :: MIT License',
    	'Natural Language :: English',
    	'Operating System :: OS Independent',
    	'Programming Language :: Python',    	
    	'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords = 'python functional higher-order',    
    packages = ['functional'],
    # Until setuptools can be trusted to do this for us, we do it in-house
	#test_suite = 'tests.all_tests',
    zip_safe = True,
)
