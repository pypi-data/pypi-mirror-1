#!/usr/bin/env python

import os
from distutils.core import setup

setup(
	name="domestos",
	version="0.101",
	description="DomestOS",
	author="Louis King",
	author_email="jinglemansweep@gmail.com",
	url="http://www.louisking.co.uk",
	packages=["domestos"],
	package_dir={"domestos": "domestos"},
	package_data={"domestos": []},
	scripts = [os.path.join("bin", "runner"),],
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
