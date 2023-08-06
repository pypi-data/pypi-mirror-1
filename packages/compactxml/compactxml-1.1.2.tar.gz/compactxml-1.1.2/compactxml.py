#!/usr/bin/env python
# John Krukoff 8/17/2009
'''
Command line utility for invoking the compactxml module on files.
'''

from __future__ import with_statement

import sys, optparse

import compactxml

optionParser = optparse.OptionParser( usage = '%prog [options] input-file [output-file]', version = '%prog ' + compactxml.__version__ )
optionParser.add_option( '-v', '--verbose', action = 'store_true', default = False, help = 'verbose output to standard error' )
optionParser.add_option( '-p', '--pretend', action = 'store_true', default = False, help = "check syntax only, don't write output" )
optionParser.add_option( '-c', '--compact', action = 'store_false', default = True, dest = 'expand', help = 'compact input to compactxml' )
optionParser.add_option( '-e', '--expand', action = 'store_true', default = True, dest = 'expand', help = 'expand input to XML (default)' )
optionParser.add_option( '-w', '--whitespace', action = 'store_true', default = False, help = 'automatic whitespace handling (stripping for compact, pretty print for expand)' )
optionParser.add_option( '-m', '--macro', help = 'file name to load default macros from' )
optionParser.add_option( '-n', '--namespace', action = 'append', help = 'default namespaces, passed in the form prefix:namespace' )

aOptions, aArguments = optionParser.parse_args( )

def input_explicit( ):
	if aArguments[ 0 ] == '-':
		return sys.stdin
	else:
		return open( aArguments[ 0 ], 'r+' if len( aArguments ) == 1 else 'r' )

def output_explicit( ):
	if aArguments[ 1 ] == '-':
		return sys.stdout
	else:
		return open( aArguments[ 1 ], 'w+' )

def output_temporary( ):
	return tempfile.TemporaryFile( mode = 'w+', prefix = 'compactxml' )

if len( aArguments ) < 1:
	optionParser.error( 'An input file name is required.' )
elif len( aArguments ) == 1:
	output_method = output_temporary
elif len( aArguments ) == 2:
	output_method = output_explicit
else:
	optionParser.error( 'At most, an input file name and optional output file name may be specified.' )

# Load macros from external file.

if aOptions.macro:
	with open( aOptions.macro , 'r' ) as macroFile:
		if aOptions.verbose:
			print >>sys.stderr, 'Opened macro file.'

		macros = compactxml.load_macros( macroFile )

		if aOptions.verbose:
			print >>sys.stderr, 'Loaded %d macros.' % len( macros )
else:
	macros = None

# Load namespaces.

aNamespaces = {}
if aOptions.namespace:
	for eNamespace in aOptions.namespace:
		prefix, namespace = eNamespace.split( ':', 1 )
		aNamespaces[ prefix ] = namespace

	if aOptions.verbose:
		print >>sys.stderr, 'Loaded %d namespace prefixes.' % len( aNamespaces )

# Expand/Compact file.

with input_explicit( ) as inputFile:
	if aOptions.verbose:
		print >>sys.stderr, 'Opened input file.'

	if aOptions.verbose:
		if aOptions.expand:
			print >>sys.stderr, 'Expanding to XML.'
		else:
			print >>sys.stderr, 'Compacting to compactxml.'

	if aOptions.pretend:
		if aOptions.expand:
			compactxml.expand( inputFile, macros = macros, namespaces = aNamespaces )
		else:
			compactxml.compact( inputFile, macros = macros, namespaces = aNamespaces, stripText = aOptions.whitespace )

		if aOptions.verbose:
			print >>sys.stderr, 'Done converting.'
	else:
		with output_method( ) as outputFile:
			if aOptions.verbose:
				print >>sys.stderr, 'Opened output file.'

			if aOptions.expand:
				compactxml.expand_to_file( inputFile, outputFile, macros = macros, namespaces = aNamespaces, prettyPrint = aOptions.whitespace )
			else:
				compactxml.compact_to_file( inputFile, outputFile, macros = macros, namespaces = aNamespaces, stripText = aOptions.whitespace )

			if aOptions.verbose:
				print >>sys.stderr, 'Done converting.'

			if aArguments == 1:
				if aOptions.verbose:
					print >>sys.stderr, 'Overwriting input file.'

				inputFile.flush( )
				inputFile.seek( 0 )
				outputFile.flush( )
				outputFile.seek( 0 )
				inputFile.write( outputfile.read( ) )
