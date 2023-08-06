#!/usr/bin/python -tt

setupArgs = {
	'name' : 'compactxml',
	'version' : '1.1.2',
	'description' : 'Parser and converter for an alternate compact XML syntax.',
	'author' : 'John Krukoff',
	'author_email' : 'python@cultist.org',
	'long_description' : '''A parser and converter for an alternate compact XML syntax, based on significant whitespace to show nesting.''',
	'keywords' : 'xml compact shorter format',
	'packages' : [ 'compactxml' ],
	}

from distutils.core import setup
setup( **setupArgs )
