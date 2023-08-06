import os
from setuptools import setup

setup(
	name = "mathomaticprimes",
	version = "0.0.1",
	author = "Josef Spillner",
	author_email = "josef.spillner@tu-dresden.de",
	description = ("Python library and web service interface (as service egg) for Mathomatic's prime number generator."),
	license = "AGPLv3",
	keywords = "primes web service egg",
	url = "http://gitorious.org/python-service-eggs",
	packages=['mathomatic'],
	long_description="Not much documented yet.",
	classifiers=[
		"Development Status :: 2 - Pre-Alpha",
		"Environment :: No Input/Output (Daemon)",
		"Programming Language :: Python :: 2",
		"Topic :: Internet :: WWW/HTTP",
		"License :: OSI Approved :: GNU Affero General Public License v3",
	],
)

