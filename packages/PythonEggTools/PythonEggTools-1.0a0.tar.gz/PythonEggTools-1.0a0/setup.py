from setuptools import setup, find_packages

version = "1.0a0"
summary = "Command line tools for working with Python packages"
long_description = """
The Python Egg Tools (PET) are command-line utilities for querying and
managing Python packages.

The tools are based upon to Debian's ``apt-get`` and ``apt-cache``
package management utilities.  They provide an alternate interface to
setuptools' ``easy_intall`` script.

``pet-get``
  A command line utility for installing, updating, and
  general management of packages.  It wraps setuptools'
  ``easy_install`` script.

``pet-cache``
  A command line utility for querying package information,  or
  for displaying all of the packages installed on the system.

"""

classifiers = [
	'Development Status :: 3 - Alpha',
	'Environment :: Console',
	'Intended Audience :: End Users/Desktop',
	'Intended Audience :: Developers',
	'Intended Audience :: System Administrators',
	'Operating System :: OS Independent',
	'Topic :: Utilities',
	'Topic :: System :: Systems Administration',
	'Programming Language :: Python'
	]

setup(
	name='PythonEggTools',
	version=version,
	description=summary,
	long_description=long_description,
	author="Maris Fogels",
    author_email="mfogels@interactdirect.com",
	license="BSD",
	#url="",
	classifiers=classifiers,
	install_requires=[],
	packages=find_packages(),
	entry_points = {
		'console_scripts': [
			'pet-get = pet.petget:main',
			'pet-cache = pet.petcache:main',
			]
		}
)
