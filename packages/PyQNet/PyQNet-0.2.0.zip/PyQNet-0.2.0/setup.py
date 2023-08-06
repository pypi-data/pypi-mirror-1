#!/usr/bin/env python
"""Installs PyQNet using distutils

Run:
	python setup.py install
to install the package from the source archive.
"""
from setuptools import setup
from sys import hexversion
if hexversion >= 0x2030000:
	# work around distutils complaints under Python 2.2.x
	extraArguments = {
		'classifiers': [
			"""License :: OSI Approved :: BSD License""",
			"""Programming Language :: Python""",
			"""Topic :: Software Development :: Libraries :: Python Modules""",
			"""Intended Audience :: Developers""",
		],
		'download_url': "https://launchpad.net/pyqnet/+download",
		'keywords': 'network,game,lightweight',
		'long_description' : """Library implementing a lightweight networking API

This library is intended to provide a simple, robust and lightweight
mechanism for producing networked Python games with reasonable
latency and low network overhead.
""",
		'platforms': ['Any'],
	}
else:
	extraArguments = {
	}

if __name__ == "__main__":
	### Now the actual set up call
	setup (
		name = "PyQNet",
		version = "0.2.0",
		description= "Quick Lightweight Networking Library for Games",
		author = "Mike C. Fletcher",
		author_email = "mcfletch@vrplumber.com",
		url = "https://launchpad.net/pyqnet",
		license = "BSD",

		package_dir = {
			'qnet':'qnet',
		},

		packages = [
			'qnet', 
		],
		
		options = {
			'sdist':{'use_defaults':0, 'force_manifest':1,'formats':['gztar','zip']},
			'bdist_rpm':{
				'group':'Libraries/Python',
				'provides':'python-qnet',
				'requires':"python",
			},
		},

		# registration metadata
		**extraArguments
	)
	
