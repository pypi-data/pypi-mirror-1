try:
	from setuptools import setup
except:
	from distutils.core import setup

setup(
    name = 'functional',
    version = '0.1',
    description = "Tools for functional programming in python",
    
    long_description = """functional provides a pure-python implementation of the C-language `functional` module that will be included in Python 2.5.
	
While the module to be shipped with python is implemented in C for speed, we've opted to rewrite this version in Python to make it more portable and easier to read.

This module will be kept 100% in sync with the capabilities offered by the C implementation. As such, the official documentation from python.org serves to document this module as well.

Currently offered: partial, a class for implementing partial function application; foldl and foldr, two functions for reducing an iterable to a single value""",
	
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
    keywords = 'python functional partial foldl foldr higher-order',    
    packages = ['functional'],
    # Until setuptools can be trusted to do this for us, we do it in-house
	#test_suite = 'tests.all_tests',
    zip_safe = True,
)
