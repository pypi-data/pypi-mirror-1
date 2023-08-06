#!/usr/bin/env python

from distutils.core import setup

from dutest import __doc__ as DESC

setup(
	name='dutest',
	version='0.1.1',
	description=DESC.split('\n', 1)[0],
	author='FLiOOPS Project',
	author_email='flioops@gmail.com',
	maintainer='Olemis Lang',
	maintainer_email='olemis@gmail.com',
	url='http://flioops.sourceforge.net',
	download_url='https://sourceforge.net/project/showfiles.php?group_id=220287',
	package_dir = {'': 'utils'},
	py_modules = ['dutest'],
	long_description= DESC
	)

