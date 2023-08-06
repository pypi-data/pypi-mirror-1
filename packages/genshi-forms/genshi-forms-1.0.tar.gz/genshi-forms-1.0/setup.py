from os.path import dirname, join
from distutils.core import setup

version = '1.0'

setup (
	name = 'genshi-forms',
	version = version,
	description = "Form generator and validator for Genshi",
	#long_description = open (join (dirname (__file__), 'README.txt')).read (),
	author = "John Millikin",
	author_email = "jmillikin@gmail.com",
	license = "GPL3",
	url = "https://launchpad.net/genshi-forms",
	download_url = "http://cheeseshop.python.org/pypi/genshi-forms/%s" % version,
	platforms = ["Platform Independent"],
	packages = ["genshi_forms", "genshi_forms.tests"],
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
)

