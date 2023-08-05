from setuptools import setup, find_packages

setup(
    name = "pickleshare",
    version = "0.1",
    py_modules = ['pickleshare','path'],
    author = "Ville Vainio",
    author_email = "vivainio@gmail.com",
    description = "Tiny 'shelve'-like database with concurrency support",
    license = "MIT",
    keywords = "database persistence pickle ipc shelve",
    long_description = """\ 
PickleShare - a small 'shelve' like datastore with concurrency support

Like shelve, a PickleShareDB object acts like a normal dictionary. Unlike shelve,
many processes can access the database simultaneously. Changing a value in 
database is immediately visible to other processes accessing the same database.

Concurrency is possible because the values are stored in separate files. Hence
the "database" is a directory where *all* files are governed by PickleShare.

Example usage::
    
    from pickleshare import *
    db = PickleShareDB('~/testpickleshare')
    db.clear()
    print "Should be empty:",db.items()
    db['hello'] = 15
    db['aku ankka'] = [1,2,313]
    db['paths/are/ok/key'] = [1,(5,46)]
    print db.keys()

This module is certainly not ZODB, but can be used for low-load 
(non-mission-critical) situations where tiny code size trumps the 
advanced features of a "real" object database.

Installation guide: easy_install pickleshare
""",
    
      entry_points = {
            'console_scripts': [
                'pickleshare = pickleshare:main',
		]
	}


)
