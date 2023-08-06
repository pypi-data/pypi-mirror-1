#!/usr/bin/env python

import os

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
	name="domestos",
	version="0.102",
	description="DomestOS",
	author="Louis King",
	author_email="jinglemansweep@gmail.com",
	url="http://www.louisking.co.uk",
	packages=["domestos"],
	package_dir={"domestos": "domestos"},
	package_data={"domestos": []},
	scripts = [os.path.join("bin", "runner"),],
	test_suite = "nose.collector",
	long_description="""DomestOS Home Automation Platform""",
	classifiers=[
		"Development Status :: 2 - Pre-Alpha",
		"Environment :: Console",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Natural Language :: English",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: Python :: 2.5",
		"Topic :: System :: Networking :: Monitoring",		
	]
)
