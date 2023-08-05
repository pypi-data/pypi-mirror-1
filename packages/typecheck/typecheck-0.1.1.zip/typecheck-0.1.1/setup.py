import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = 'typecheck',
    version = '0.1.1',
    description = 'A type-checking module for Python',
    long_description = """
    A type-checking module for Python.
    
    This module was a strawman for a discussion about
    static typing around the time that the BDFL was talking
    about including it in an upcoming version of Python.""",
    author = 'Iain Lowe',
    author_email = 'ilowe@cryogen.com',
    url = 'http://www.schmeez.org/software/typecheck',
    license = 'MIT License',
    classifiers = [
    	'Development Status :: 4 - Beta',
    	'Intended Audience :: Developers',
    	'License :: OSI Approved :: MIT License',
    	'Natural Language :: English',
    	'Operating System :: OS Independent',
    	'Programming Language :: Python',    	
    	'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords = 'python decorator type-check typesafe typesafety type typing static',    
    packages = find_packages(),
    py_modules = ['typecheck', 'ez_setup'],
    test_suite = 'typecheck._TestSuite',
    zip_safe = True,    
)
