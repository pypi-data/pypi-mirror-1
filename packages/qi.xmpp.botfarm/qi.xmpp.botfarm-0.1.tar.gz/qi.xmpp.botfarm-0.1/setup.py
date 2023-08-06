from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='qi.xmpp.botfarm',
	  version=version,
	  description="A twisted server supporting multiple xmpp helpdesk bots.",
	  long_description=open("README.txt").read() + "\n" +
					   open(os.path.join("docs", "HISTORY.txt")).read(),
	  # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
	  classifiers=[
		"Programming Language :: Python",
		"Topic :: Software Development :: Libraries :: Python Modules",
		],
	  keywords='xmpp twisted bot jabber helpdesk',
	  author='G. Gozadinos',
	  author_email='ggozad@qiweb.net',
	  url='http://chatblox.com',
	  license='GPL',
	  packages=find_packages(exclude=['ez_setup']),
	  namespace_packages=['qi', 'qi.xmpp'],
	  include_package_data=True,
	  zip_safe=False,
	  install_requires=[
		  'setuptools','elementtree',
		  # -*- Extra requirements: -*-
	  ],
	  entry_points={
		'console_scripts':[
			'botfarm = qi.xmpp.botfarm.main:main',
		]},
	  )
