#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = 'EatLint',
    version = '1.0.1',
    description = 'PyLint Summary and Graph Generators for Bitten.',
    long_description = '''
EatLint is a Trac__ plugin that adds a lint report summarizer and a lint chart to
Bitten__.  This means that when a Bitten build that includes a lint step
the output can not only be captured but reported on. The report shows
the number of problems per file by category: convention, refactor,
error, and warning as well as showing the totals for each file, for each
category, and a grand-total showing the state of the entire project.
Similarly the chart plugin charts the total number of problems as well
as individual lines for each category. This gives you an idea of the
readability of your project's code over time.

__ http://trac.edgewall.org
__ http://bitten.edgewall.org

EatLint's code and templates are based on the code and templates provided by the Bitten project for coverage and unittest data.  The Bitten code and templates are provided under a BSD-style license and so is this plugin.  Please see License__ for a copy of the license.

__ http://echospiral.com/trac/eatlint/wiki/License

An example build recipe can be found on the wiki__.

__ http://echospiral.com/trac/eatlint/wiki

Installation:

Installation is done just as for any other Trac plugin.  Using the
easy_install command from setuptools is the easiest (provided you have
already setuptools installed)::

    easy_install eatlint

After that you must configure your Trac project to use the plugin.  Edit
conf/trac.ini in your Trac directory to include this::

    [components]
    eatlint.* = enabled
''',
    author = 'Jeffrey Kyllo',
    author_email = 'jkyllo-eatlint@echospiral.com',
    packages = find_packages(),
    package_data = {
	'eatlint': ['templates/*.cs'],
    },
    entry_points = {
	'trac.plugins': [
	    'eatlint.lint = eatlint.lint',
	    ]
    },
    zip_safe = False,
    url = 'https://echospiral.com/trac/eatlint',
    keywords = 'trac,bitten,lint,pylint',
#    install_requires = [
#	'trac',
#    ],
#    dependency_links = [
#	#'http://bitten.edgewall.org',
#	'http://svn.edgewall.org/repos/bitten/',
#    ],
    classifiers = [
	'Programming Language :: Python',
	'Operating System :: OS Independent',
	'License :: OSI Approved :: BSD License',
	'Natural Language :: English',
    ],
)
