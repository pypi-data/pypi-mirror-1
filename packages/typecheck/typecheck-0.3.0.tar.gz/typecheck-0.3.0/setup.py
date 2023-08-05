import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = 'typecheck',
    version = '0.3.0',
    description = 'A runtime type-checking module for Python',
    
    long_description = """
    A runtime type-checking module for Python supporting both parameter-type checking
    and return-type checking for funcitons, methods and generators.

	The main workhorses of this module, the functions typecheck_args and typecheck_return, are used as function/method decorators. A typecheck_yield decorator provides a mechanism to typecheck the values yielded by generators.

	Three utility classes, And(), Or() and Not() are provided to assist in building more complex signatures by creating boolean expressions based on classes and/or types. A similar class, Any(), can be used to indicate that you don't care about the type of the object.
	
	The module also includes support for type variables, a concept borrowed from languages such as Haskell.

	Note that typechecking can be {en,dis}abled at runtime by toggling the typecheck.enable_checking global boolean; a value of True (the default) causes all typechecks (both for parameters and return values) to be run, while False disables them.""",
	
    author = 'Collin Winter, Iain Lowe',
    author_email = 'collinw@gmail.com, ilowe@cryogen.com',
    url = 'http://www.ilowe.net/software/typecheck',
    license = 'MIT License',
    classifiers = [    	
    	'Intended Audience :: Developers',
    	'License :: OSI Approved :: MIT License',
    	'Natural Language :: English',
    	'Operating System :: OS Independent',
    	'Programming Language :: Python',    	
    	'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords = 'python decorator type-check typesafe typesafety type typing static',    
    packages = find_packages(),    
    # Until setuptools can be trusted to do this for us, we do it in-house
	#test_suite = 'tests.all_tests',
    zip_safe = True,
)
