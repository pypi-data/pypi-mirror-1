#!/usr/bin/python -tt
'''
compactxml is a module for converting from and to a python like dialect of XML.

Use the expand* functions to convert from compactxml to XML, and the compact* functions to convert from XML to compactxml.
'''

from __future__ import absolute_import

from lxml import etree

import cStringIO as StringIO

from .expand import expand as expand_string
from .expand import load_macros as expand_load_macros
from .compact import compact as compact_file
from .resolve import resolve_filename

def resolve( location ):
	'''
	A global function used in expand calls to lookup files specified by
	?load preprocessor directives in compactxml files. Override this
	function to change how file names are looked up. By default, loads as
	local file name.

	Arguments:
	location -- The path to resolve.

	Returns: An open file object.
	'''
	return resolve_filename( location )

def load_macros( document, macros = None ):
	'''
	Loads macros from a given compactxml document. Accepts strings or file
	objects. Used to load macros to be used in expanding other compactxml
	files.

	Arguments:
	document -- Document to load macros from.
	macros -- Already loaded macros to combine with those loaded.

	Returns: An opaque macro object.
	'''
	if isinstance( document, basestring ):
		return expand_load_macros( document, macros )
	else:
		return expand_load_macros( document.read( ), macros )

def expand( document, macros = None, namespaces = {} ):
	'''
	Expands a compactxml document into a parsed lxml ElementTree. Accepts
	strings or file objects.

	Arguments:
	document -- Document to expand.
	macros -- Optional default macros to use during the expand, as loaded by load_macros.
	namespaces -- Optional dictional of default prefixes and namespaces to use dureing the expand.

	Returns: An lxml ElementTree object.
	'''
	if isinstance( document, basestring ):
		return expand_string( document, macros, namespaces )
	else:
		return expand_string( document.read( ), macros, namespaces )

def expand_to_string( document, macros = None, namespaces = {}, prettyPrint = False ):
	'''
	Expands a compactxml document as expand, however returns a serialized
	string of the expanded XML. Accepts strings or file objects.

	Arguments:
	document -- Document to expand.
	macros -- Optional default macros to use during the expand, as loaded by load_macros.
	namespaces -- Optional dictional of default prefixes and namespaces to use dureing the expand.
	prettyPrint -- Optional flag for pretty printing the resulting XML. Defaults to false.

	Returns: A string.
	'''
	return etree.tostring( expand( document, macros, namespaces ), pretty_print = prettyPrint )

def expand_to_file( document, outputFile, macros = None, namespaces = {}, prettyPrint = False ):
	'''
	Expands a compactxml document as expand, however writes a serialized
	string of the expanded XML to the given open file object. Accepts
	strings or file objects.

	Arguments:
	document -- Document to expand.
	outputFile -- Open file object to write output to.
	macros -- Optional default macros to use during the expand, as loaded by load_macros.
	namespaces -- Optional dictional of default prefixes and namespaces to use dureing the expand.
	prettyPrint -- Optional flag for pretty printing the resulting XML. Defaults to false.

	Returns: Nothing.
	'''
	outputFile.write( expand_to_string( document, macros, namespaces, prettyPrint ) )

def compact( document, macros = None, namespaces = {}, stripText = False ):
	'''
	Compacts a serialized XML string or file to compactxml form.

	Arguments:
	document -- Document to compact.
	macros -- Currently unused.
	namespaces -- Current unused.
	stripText -- Optional flag for stripping all text before compacting,
	to remove extraneous whitespace. Defaults to false.

	Returns: A string
	'''
	if isinstance( document, basestring ):
		return compact_file( StringIO.StringIO( document ), macros, namespaces, stripText )
	else:
		return compact_file( document, macros, namespaces, stripText )

compact_to_string = compact

def compact_to_file( document, outputFile, macros = None, namespaces = {}, stripText = False ):
	'''
	Compacts a serialized XML string or file to compactxml form, writing
	the resulting string to an open file.

	Arguments:
	document -- Document to compact.
	outputFile -- Open file object to write output to.
	macros -- Currently unused.
	namespaces -- Current unused.
	stripText -- Optional flag for stripping all text before compacting,
	to remove extraneous whitespace. Defaults to false.

	Returns: Nothing.
	'''
	outputFile.write( compact_to_string( document, macros, namespaces, stripText ) )
