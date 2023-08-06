import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
	name = 'simplui',
	version = '1.0.3',
	author = 'Tristam MacDonald',
	author_email = 'swiftcoder@gmail.com',
	description = 'Light-weight GUI toolkit for pyglet',
	url = 'http://wiki.darkcoda.com/wiki/simplui/',
	platforms = ['all'],
	license = 'BSD',
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
		'Topic :: Scientific/Engineering :: Human Machine Interfaces',
		'Topic :: Software Development :: User Interfaces',
	],
	
	packages = find_packages(),
	install_requires = ['simplejson >= 2.0', 'pyglet>=1.1']
)
