from os.path import dirname, join
try:
	from setuptools import setup, Extension
except ImportError:
	from distutils.core import setup, Extension
	
# If you change the version here, also change it in jsonlib2.c and .py.
version = '1.5.2'

setup (
	name = 'jsonlib2',
	version = version,
	description = "JSON serializer/deserializer for Python",
	long_description = open (join (dirname (__file__), 'README.txt')).read (),
	author = "Alec Flett",
	author_email = "alecf@flett.org",
	license = "MIT",
	url = "http://code.google.com/p/jsonlib2/",
	download_url = "http://code.google.com/p/jsonlib2/downloads/list",
	platforms = ["Platform Independent"],
    test_suite = "jsonlib2_simplejson.tests",
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: Software Development :: Libraries :: Python Modules",
	],
	keywords = ["json"],
	ext_modules = [
		Extension ('jsonlib2', ['jsonlib2.c']),
	],
)
