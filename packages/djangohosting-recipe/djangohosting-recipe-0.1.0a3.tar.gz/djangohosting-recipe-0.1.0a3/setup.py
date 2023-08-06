import os

from setuptools import setup, find_packages

version = '0.1.0a3'

def read_file(name):
	return open(os.path.join(os.path.dirname(__file__), name)).read()

readme = read_file('README.txt')

setup(name='djangohosting-recipe',
	version=version,
	description="Buildout recipe for Djangohosting.ch",
	long_description='\n\n'.join([readme]),
	classifiers=[
		'Framework :: Buildout',
		'Framework :: Django',
		'Topic :: Software Development :: Build Tools',
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: BSD License',
		'Operating System :: MacOS :: MacOS X',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX',
		],
	package_dir={'': 'src'},
	packages=find_packages('src'),
	keywords='',
	author='Damien Lebrun',
	author_email='dinoboff@hotmail.com',
	url='http://code.google.com/p/djangohosting-recipe/',
	license='BSD',
	zip_safe=False,
	install_requires=[
		'zc.buildout',
		'zc.recipe.egg',
		'djangorecipe'
	],
	entry_points="""
	# -*- Entry points: -*-
	[zc.buildout]
	default = djangohosting.recipe:Recipe
	""",
	)
