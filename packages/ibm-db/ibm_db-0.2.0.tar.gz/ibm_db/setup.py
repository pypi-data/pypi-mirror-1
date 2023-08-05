import os
import sys

from setuptools import setup, find_packages
from distutils.core import setup, Extension


try:
	ibm_db_dir = os.environ['IBM_DB_DIR']
	ibm_db_lib = os.environ['IBM_DB_LIB']
except (KeyError):
	print 'IBM DataServer environment not set. Please refer to the README for more information on building the driver'
	quit()

library = ['db2']
if (sys.platform[0:3] == 'win'):
  library = ['db2cli']

ibm_db = Extension('ibm_db',
                    include_dirs = [ibm_db_dir + '/include'],
                    libraries = library,
                    library_dirs = [ibm_db_lib],
                    sources = ['ibm_db.c'])

modules = ['config', 'ibm_db_dbi', 'testfunctions', 'tests']

setup (name = 'ibm_db',
       version = '0.2.0',
       description = 'Python DBI driver for DB2 (LUW, zOS, i5) and IDS',
       ext_modules = [ibm_db],
       py_modules = modules,
       packages = find_packages(),
       author = 'IBM Application Development Team',
       author_email = 'opendev@us.ibm.com',
       url = 'http://www.python.org/doc/current/ext/building.html',
       long_description = '''
This extension is the implementation of Python Database API Specification v2.0. The extension supports DB2 (LUW, zOS, i5) and IDS (Informix Dynamic Server)
'''
      )


