from os.path import dirname, join
from setuptools import setup, Extension

version = '1.1.3'

setup (
	name = 'django-genshi',
	version = version,
	description = "Django integration for Genshi",
	long_description = open (join (dirname (__file__), 'README.txt')).read (),
	author = "John Millikin",
	author_email = "jmillikin@gmail.com",
	license = "GPL",
	url = "https://launchpad.net/django-genshi",
	download_url = "http://pypi.python.org/pypi/django-genshi/%s" % version,
	platforms = ["Platform Independent"],
	packages = ['django_genshi', 'django_genshi.loaders'],
	classifiers = [
		"Development Status :: 4 - Beta",
		"Framework :: Django",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Text Processing :: Markup :: HTML",
		"Topic :: Text Processing :: Markup :: XML",
	],
	keywords = ["django", "genshi"],
	install_requires = [
		"Django>=1.0_final",
		"Genshi>=0.5.1",
	],
)
