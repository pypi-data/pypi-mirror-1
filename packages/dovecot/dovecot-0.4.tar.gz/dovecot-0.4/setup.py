#!/usr/bin/env python

# Copyright 2009 Thomas Arnett
# Licensed under the Open Software License, Version 3.0

import glob	
import os.path
from setuptools import setup, find_packages

setup(
	name = 'dovecot',
	version = '0.4',
	author = 'Thomas Arnett',
	author_email = 'tom@misfeature.net',
	description = 'Library and scripts for Dovecot SASL integration',
	long_description = '''
The Dovecot IMAP/POP server can authenticate against various databases. It also 
implements SASL, enabling other programs to authenticate through Dovecot. This 
package provides a Python interface to the Dovecot Authentication Protocol and 
a connector for jabberd2.
''',
	license = 'OSL-3.0',
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved',
		'Operating System :: POSIX',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 3.0',
		'Topic :: System :: Systems Administration :: Authentication/Directory',
	],
	package_dir = {'': 'lib'},
	packages = find_packages('lib'),
	scripts = glob.glob(os.path.join('bin', '*')),
)
