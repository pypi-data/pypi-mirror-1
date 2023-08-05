try:
	from setuptools import setup
except:
	from distutils.core import setup

setup(
    name = 'svnmock',
    version = '0.1',
    description = "Testing library for Subversion's python bindings",
    
    long_description = """svnmock provides capabilities to emulate the entire python language API for the Subversion revision control system.
	
The purpose of this library is to make it easy for developers to verify that SVN-facing code is working correctly. svnmock provides tools to assert that certain API functions must be called in a certain order with certain parameters, and that certain values should be returned from those function calls.

In addition, svnmock allows assertions of the type, "the return value from api_func_1() must be given as a parameter to api_func_2() and api_func_3()". This allows more fine-grained flow control tracking than simple "was the 4th parameter '6'?" assertions.

In addition to simple "was function X called with arguments Y and Z?" assertions, svnmock provides easy mechanisms for simulating tricky failure conditions that might otherwise be impossible -- or at least, very difficult -- to simulate otherwise.""",
	
    author = 'Collin Winter',
    author_email = 'collinw@gmail.com',
    url = 'http://oakwinter.com/code/svnmock',
    license = 'MIT License',
    classifiers = [    	
    	'Intended Audience :: Developers',
    	'License :: OSI Approved :: MIT License',
    	'Natural Language :: English',
    	'Operating System :: OS Independent',
    	'Programming Language :: Python',    	
    	'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords = 'subversion svn testing mock',
    packages = ['svnmock'],
    # Until setuptools can be trusted to do this for us, we do it in-house
	#test_suite = 'tests.all_tests',
    zip_safe = True,
)
