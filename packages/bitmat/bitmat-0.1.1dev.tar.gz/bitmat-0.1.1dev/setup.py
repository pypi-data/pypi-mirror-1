from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(name='bitmat',
	version=version,
	description="BitMat Index for RDFLib",
	long_description="""\
	BitMat Index for RDFLib""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='rdf bitmat triplestore index',
	author='William Waites',
	author_email='wwaites_at_gmail.com',
	url='',
	license='BSD',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		"bitmagic",
		"swiss",
		"nose",
	],
	entry_points="""
	# -*- Entry points: -*-
	""",
)
