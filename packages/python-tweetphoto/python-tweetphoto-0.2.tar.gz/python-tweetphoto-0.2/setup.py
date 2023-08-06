#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# The setup and build script for the python-tweetphoto library.

# Copyright (c) 2010/2009, Marcel Caraciolo
# caraciol@gmail.com
# twitter: marcelcaraciolo

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

__author__ = 'caraciol@gmail.com'
__version__ = '0.2'


# The base package metadata to be used by both distutils and setuptools
METADATA = dict(
	name = "python-tweetphoto",
	version = __version__,
	packages = ['pyTweetPhoto'],
	author='Marcel Caraciolo',
	author_email='caraciol@gmail.com',
	description='A python wrapper around the TweetPhoto API',
	license='GNU Library or Lesser General Public License (LGPL)',
	url='http://code.google.com/p/python-tweetphoto/',
	download_url= 'http://python-tweetphoto.googlecode.com/files/pyTweetPhoto-0.2.zip',
	keywords='tweetphoto api',
)

# Extra package metadata to be used only if setuptools is installed
SETUPTOOLS_METADATA = dict(
	install_requires = ['setuptools', 'simplejson'],
	include_package_data = True,
	classifiers = [
	'Development Status :: 2 - Pre-Alpha',
	'Programming Language :: Python',
	'Intended Audience :: Developers',
	'Operating System :: OS Independent',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
	'Topic :: Software Development :: Libraries :: Python Modules',
	'Topic :: Communications :: File Sharing',
	'Topic :: Multimedia :: Graphics',
	'Topic :: Internet',
  ],
)




def Main():
	
	# Use setuptools if available, otherwise fallback and use distutils
	try:
		import setuptools
		METADATA.update(SETUPTOOLS_METADATA)
		setuptools.setup(**METADATA)
	except ImportError:
		import distutils.core
		distutils.core.setup(**METADATA)


if __name__ == '__main__':
	Main()