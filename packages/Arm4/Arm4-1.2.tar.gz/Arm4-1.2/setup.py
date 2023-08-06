#!/usr/bin/env python

try:
	from setuptools import setup, Extension
except:
	from distutils.core import setup, Extension

module1 = Extension('arm4',
                    define_macros = [('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '2')],
                    libraries = ['arm4'],
                    sources = ['arm4module.c'])

setup (name = 'Arm4',
       version = '1.2',
       description = 'Application Response Measurement (ARM) Version 4.0',
       author = 'David Carter',
       author_email = 'dcarter@arm4.org',
       url = 'http://www.arm4.org/',
       download_url = 'http://sourceforge.net/projects/arm4/',
       license = 'Eclipse Public License v1.0',
       long_description = '''
Python language bindings for the Application Response Measurement (ARM) Version 4.0 standard.

This module provides a Python language implementation of the ARM 4.0
standard. At it's simplest, it's a straight exposure of the C language
bindings with enough concessions to make it fit the Python language.

Usage:

  import arm4

  # Register
  app_id = arm4.register_application ("Python test")
  tran_id = arm4.register_transaction (app_id, "Python hello world")

  # Start our application and transaction measurements
  app_handle = arm4.start_application (app_id, "Example")
  tran_handle = arm4.start_transaction (app_handle, tran_id)

  # Do our work
  print 'Hello, world!'

  # Stop our measurements
  arm4.stop_transaction (tran_handle) # Default status is arm4.ARM_STATUS_GOOD
  arm4.stop_application (app_handle)

  # Finish up
  arm4.destroy_application (app_id)

This is a simple example that doesn't make use of ARM's advanced
correlators or metrics. More examples can be found at http://www.arm4.org

This module is based on the ARM Issue 4.0, Version 2 - C Binding standard. More information
can be found at http://www.opengroup.org/management/arm.htm
''',
       classifiers = ['Development Status :: 5 - Production/Stable',
                      'Intended Audience :: Developers',
                      'Intended Audience :: Information Technology',
                      'License :: OSI Approved',
                      'Operating System :: OS Independent',
                      'Programming Language :: Python',
                      'Topic :: Software Development',
                      'Topic :: Software Development :: Libraries :: Python Modules',
                      'Topic :: Software Development :: Quality Assurance',
                      'Topic :: Software Development :: Testing',
                      'Topic :: System :: Distributed Computing',
                      'Topic :: System :: Monitoring'],
       ext_modules = [module1])

