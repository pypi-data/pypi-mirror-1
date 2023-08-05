try:
	from setuptools import setup
except:
	from distutils.core import setup

setup(
    name = 'functional',
    version = '0.5',
    description = "Tools for functional programming in python",
    
    long_description = """functional provides Python users with numerous
tools common in functional programming, such as foldl, foldr, flip, as well
as mechanisms for partial function application and function composition.

functional comes in two flavours: one is written in a combination of C and
Python, focusing on performance. The second is written in pure Python and
emphasises code readability and portability. The pure-Python variant is also
recommended if your setup does not allow compilation of third-party extension
modules.""",
	
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
