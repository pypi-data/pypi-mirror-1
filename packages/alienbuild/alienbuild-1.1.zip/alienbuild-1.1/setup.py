################################################################################
#
# (C) Falling Down Games, Inc.  2007
#
# AlienBuild - A large code and asset build system written in python
#
################################################################################

from distutils.core import setup
import os

setup (
	name             = 'alienbuild',
	version          = '1.1',
	description      = 'A large code and asset build system written in python.',
	author           = 'Patrick Crawley and Charles Mason',
	author_email     = 'pncrawley@gmail.com',
	license          = 'GNU General Public License (GPL)',
	long_description = 'A large code and asset build system written in python.',
	url              = 'http://www.chelestra.com/~crawley/alienbuild_web/home.py',
	download_url     = 'http://pypi.python.org/pypi?%3Aaction=search&term=alienbuild&submit=search',
	packages         = [ 'alienbuild' ],
	package_data     = { 'alienbuild' : [ 'LICENSE' ] },
	classifiers      = [
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Programming Language :: Python',
		'Topic :: Software Development',
		'Topic :: Software Development :: Build Tools',
	],
)

