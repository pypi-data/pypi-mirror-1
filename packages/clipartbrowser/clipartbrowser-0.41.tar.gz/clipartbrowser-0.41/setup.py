#!/usr/bin/python
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

setup(
	name = 'clipartbrowser',
	version = '0.41',
	description = 'GTK interface for browsing and searching clip art',
        long_description = '''An application for searching and browsing clip art, written with Python and GTK.  It can connect to multiple clip art sources and aggregate their results.  Out of the box, it connects to the Open Clip Art Library and local clip art, but plugins to connect to other clip art sources can be written with easy.  Requires Python >= 2.4, PyGTK >= 2.6.''',
	author = 'Greg Steffensen',
	author_email = 'greg.steffensen@gmail.com',
	license = 'GPL',
	keywords = 'clipart graphics art svg',
	packages = ['ClipartBrowser', 'ClipartBrowser.repositories'],
	package_data = {'':['*.glade', '*.png'], 'ClipartBrowser/repositories':['*.glade']},
        entry_points = {
            'console_scripts':['clipartbrowser = ClipartBrowser.browser:run']
        },
	zip_safe = True,
)
