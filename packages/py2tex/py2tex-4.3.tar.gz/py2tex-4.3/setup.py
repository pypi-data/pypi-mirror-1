#!/usr/bin/env python

from distutils.core import setup

setup_dict = {
	'name': "py2tex",
	'version': "4.3",
	'description': "Format Python code in TeX",
	'author': "Jeroen van Maanen",
	'author_email': "jeroenvm@xs4all.nl",
	'url': "http://www.sollunae.net/py2tex/",
	'py_modules': ['py2tex', 'struct2latex', 'StructuredText'],
	'scripts': ['py2tex'],
}

if __name__ == '__main__':
	apply(setup, (), setup_dict)
