from setuptools import setup, find_packages

setup(
	name = 'cifilter',
	version = '0.3dev',
	packages = find_packages(exclude = [ 'tests' ]),
	include_package_data = True,
	scripts = ['scripts/cifilter'],
	zip_safe = True,
	author = 'Jonathan Wight',
	author_email = 'jwight@mac.com',
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Environment :: MacOS X :: Cocoa',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: MacOS :: MacOS X',
		'Programming Language :: Objective C',
		'Topic :: Multimedia :: Graphics',
		'Topic :: Multimedia :: Graphics :: Editors :: Raster-Based',
		'Topic :: Software Development',
		],
	description = 'CoreImage command line tool',
	license = 'BSD License',
	long_description = file('README.txt').read(),
	platforms = 'Mac OS X',
	url = 'https://bitbucket.org/schwa/cifilter/',
	)

