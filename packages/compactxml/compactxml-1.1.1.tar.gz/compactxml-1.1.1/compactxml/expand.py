#!/usr/bin/python -tt

from __future__ import absolute_import

import re, operator, copy

from lxml import etree

import pyparsing
from . import pyparsingaddons as addons
from .macro import Macros

# Global parsers, as used for macro parsing.
name = pyparsing.Regex( r'[_\w][-_.\w]*', re.U )
processingInstructionTarget = pyparsing.Regex( r'[_\w:][-_.\w:]*', re.U )
prefix = name
xmlName = pyparsing.Group( pyparsing.Optional( prefix + pyparsing.Literal( ':' ).suppress( ) ) + name )

def create_grammar( ):
	# Global values for grammar. Use function scope to create thread
	# safety.
	aIndentations = [ 1 ]
	aIndentationStack = []

	def push_indent( ):
		aIndentationStack.append( aIndentations[ : ] )
		aIndentations[ : ] = [ 1 ]
		return []

	def pop_indent( ):
		aIndentations[ : ] = aIndentationStack.pop( )
		return []

	# Avoid setting default, as causes problems for other pyparsing
	# modules.
	#pyparsing.ParserElement.setDefaultWhitespaceChars( ' \t' )

	# Duplicate global parsers, to avoid exponential parsing time growth.
	name = pyparsing.Regex( r'[_\w][-_.\w]*', re.U )
	processingInstructionTarget = pyparsing.Regex( r'[_\w:][-_.\w:]*', re.U )
	prefix = name
	xmlName = pyparsing.Group( pyparsing.Optional( prefix + pyparsing.Literal( ':' ).suppress( ) ) + name )
	macroName = xmlName.copy( ).setParseAction( lambda tokens: [ ':'.join( tokens[ 0 ] ) ] )

	anyValue = pyparsing.CharsNotIn( '\r\n' )
	continuation = pyparsing.LineEnd( ) + pyparsing.FollowedBy( '\\' ) + addons.checkIndent( aIndentations ) + '\\'
	continuation.setParseAction( pyparsing.replaceWith( '\n' ) )
	multilineValue = pyparsing.OneOrMore( anyValue | continuation )
	multilineValue.setParseAction( lambda tokens: [ ''.join( tokens ) ] )
	optionalMultilineValue = pyparsing.Optional( multilineValue, default = '' )
	whitespace = pyparsing.OneOrMore( pyparsing.Word( ' \t' ) ).suppress( )

	unquotedValue = pyparsing.CharsNotIn( ' \t\r\n' )
	singleQuotedValue = pyparsing.QuotedString( quoteChar = "'", escQuote = "''" )
	doubleQuotedValue = pyparsing.QuotedString( quoteChar = '"', escQuote = '""' )
	value = singleQuotedValue | doubleQuotedValue | unquotedValue

	assignment = pyparsing.Literal( '=' ).suppress( )

	variable = pyparsing.Group( '@' + xmlName )
	variableDefinition = pyparsing.Group( variable + pyparsing.Optional( assignment + value ) )
	constant = pyparsing.Group( pyparsing.Empty( ).setParseAction( pyparsing.replaceWith( '"' ) ) + value )
	combiner = pyparsing.Literal( '+' ).suppress( )
	expressionValue = pyparsing.Group( pyparsing.ZeroOrMore( variable + combiner | constant + combiner ) + ( variable | constant ) )

	def literal_list( characters ):
		literalExpression = pyparsing.And( [ pyparsing.Literal( eCharacter ) for eCharacter in characters ] )
		literalExpression = pyparsing.Combine( literalExpression, adjacent = False )

		return literalExpression

	def create_statements( ):
		prefixedNamespace = '#' + prefix + assignment - value
		defaultNamespace = '#' + value
		emptyDefaultNamespace = '#'
		inlineNamespace = prefixedNamespace | defaultNamespace | emptyDefaultNamespace

		fullAttribute = '@' + xmlName + assignment - value
		defaultAttribute = '@' + xmlName
		inlineAttribute = fullAttribute | defaultAttribute

		processing = literal_list( '<?' ) + processingInstructionTarget + whitespace + optionalMultilineValue
		namespace = prefixedNamespace | defaultNamespace | emptyDefaultNamespace
		attribute = fullAttribute | defaultAttribute
		text = '"' + optionalMultilineValue
		restartIndentation = pyparsing.Literal( '<' ).setParseAction( push_indent ).suppress( )
		resumeIndentation = pyparsing.Literal( '>' ).setParseAction( pop_indent ).suppress( )
		comment = '!' + optionalMultilineValue
		element = '<' + xmlName + pyparsing.ZeroOrMore( pyparsing.Group( inlineNamespace ) | pyparsing.Group( inlineAttribute ) )

		attributeGroup = '@@' + macroName
		macroParameters = pyparsing.ZeroOrMore( pyparsing.Group( inlineNamespace ) | pyparsing.Group( inlineAttribute ) | pyparsing.Group( pyparsing.Empty( ).setParseAction( pyparsing.replaceWith( '$' ) ) + value ) )
		macro = pyparsing.Empty( ).setParseAction( pyparsing.replaceWith( '$$$' ) ) + macroName + macroParameters 

		return processing, namespace, attribute, text, restartIndentation, resumeIndentation, comment, element, attributeGroup, macro

	processing, namespace, attribute, text, restartIndentation, resumeIndentation, comment, element, attributeGroup, macro = create_statements( )

	def create_macro_statements( ):
		prefixedNamespace = literal_list( '$#' ) + expressionValue + assignment + expressionValue
		defaultNamespace = literal_list( '$#' ) + expressionValue
		inlineNamespace = prefixedNamespace | defaultNamespace

		fullAttribute = literal_list( '$@' ) + expressionValue + assignment + expressionValue
		defaultAttribute = literal_list( '$@' ) + expressionValue
		inlineAttribute = fullAttribute | defaultAttribute

		processing = literal_list( '$<?' ) + expressionValue + expressionValue
		namespace = prefixedNamespace | defaultNamespace
		attribute = fullAttribute | defaultAttribute
		text = literal_list( '$"' ) + expressionValue
		comment = literal_list( '$!' ) + expressionValue
		element = literal_list( '$<' ) + expressionValue
		contents = literal_list( '$$' )

		return processing, namespace, attribute, text, comment, element, contents

	processingMacro, namespaceMacro, attributeMacro, textMacro, commentMacro, elementMacro, contentsMacro = create_macro_statements( )

	endStatement = pyparsing.OneOrMore( pyparsing.LineEnd( ).suppress( ) )

	doctype = literal_list( '<!' ) + 'DOCTYPE' - multilineValue

	loadPreprocess = pyparsing.Literal( '?' ) + 'load' - value
	defaultAttributePreprocess = pyparsing.Literal( '?' ) + 'default' - pyparsing.Optional( value, default = '' )
	attributePreprocessDefinition = pyparsing.Literal( '?' ) + 'attribute' - macroName + pyparsing.Group( pyparsing.Empty( ) )
	elementPreprocessDefinition = pyparsing.Literal( '?' ) + 'element' - macroName + pyparsing.Group( pyparsing.ZeroOrMore( variableDefinition ) )

	def create_block( simple, compound ):
		block = pyparsing.Forward( )
		simpleStatement = simple + endStatement
		compoundStatement = compound + endStatement + pyparsing.Optional( block )
		statement = compoundStatement | simpleStatement
		block << addons.indentedBlock( statement, aIndentations )
		block.setParseAction( lambda tokens: tokens[ 0 ] )
		return compoundStatement

	simple = processing | comment | restartIndentation | resumeIndentation | namespace | attribute | text | defaultAttributePreprocess | attributeGroup
	compound = element | macro
	compoundStatement = create_block( simple, compound )

	def create_single_block( simple, compound ):
		statement = simple + endStatement
		block = addons.indentedBlock( statement, aIndentations )
		block.setParseAction( lambda tokens: tokens[ 0 ] )
		compoundStatement = compound + endStatement + pyparsing.Optional( block )
		return compoundStatement

	simple = namespace | attribute
	attributePreprocess = create_single_block( simple, attributePreprocessDefinition )

	simple = processing | comment | restartIndentation | resumeIndentation | namespace | attribute | text | defaultAttributePreprocess | attributeGroup | processingMacro | namespaceMacro | attributeMacro | textMacro | commentMacro | contentsMacro
	compound = element | elementMacro | macro
	elementCompoundStatement = create_block( simple, compound )
	elementPreprocess = elementPreprocessDefinition + endStatement + pyparsing.Group( pyparsing.Optional( elementCompoundStatement ) )

	def top_level_block( statement ):
		block = addons.indentedBlock( statement, aIndentations, False )
		block.setParseAction( lambda tokens: tokens[ 0 ] )
		return block

	preprocessingStatement = top_level_block( loadPreprocess + endStatement | defaultAttributePreprocess + endStatement | attributePreprocess | elementPreprocess )
	doctypeStatement = pyparsing.Group( addons.checkIndent( aIndentations ) + doctype + endStatement )
	topLevelStatement = top_level_block( ( processing | comment ) + endStatement )
	rootStatement = pyparsing.Group( addons.checkIndent( aIndentations ) + compoundStatement )
	grammar = pyparsing.Optional( endStatement ) + pyparsing.Optional( preprocessingStatement ) + pyparsing.Optional( doctypeStatement ) + pyparsing.Optional( topLevelStatement ) + rootStatement + pyparsing.Optional( topLevelStatement ) + pyparsing.StringEnd( ).suppress( )

	# Set all whitespace values.
	addons.setWhitespace( grammar, ' \t' )
	# Reset whitespace exceptions.
	anyValue.setWhitespaceChars( '' )
	multilineValue.setWhitespaceChars( '' )
	optionalMultilineValue.setWhitespaceChars( '' )
	whitespace.setWhitespaceChars( '' )

	grammar.parseWithTabs( )

	return grammar

def scope_iter( scope ):
	for statement in scope:
		if not statement:
			continue

		type = statement[ 0 ]

		yield statement, type

def lookahead_iter( scope, aMacros ):
	for statement in scope[ 2 : ]:
		if not statement:
			continue

		type = statement[ 0 ]
		if type == '@@':
			assert len( statement ) == 2
			name = statement[ 1 ]
			expansion = aMacros.attribute( name )[ 1 ]
			if expansion is None:
				aStatements = []
			else:
				aStatements = expansion
		else:
			aStatements = [ statement ]

		for statement in aStatements:
			if not statement:
				continue

			type = statement[ 0 ]

			#print 'iter:', statement
			yield statement, type

def expand_macro( statement, aMacros, defaultAttributeValue ):
	while True:
		assert statement[ 0 ] == '$$$', 'Statement to expand must be a macro.'
		name = statement[ 1 ]
		aDefinedParameters, expansion = aMacros.element( name )
		aParameters, aExtra = macro_lookahead( statement, aDefinedParameters, aMacros, defaultAttributeValue )
		if expansion is None:
			statement = []
		else:
			statement = expansion[ 0 ]

		aExpanded = parse_macro( [ statement ], aParameters, aExtra )
		assert len( aExpanded ) == 1
		statement = aExpanded[ 0 ]

		# Recursively expand if replacement statement is also a macro.
		if statement[ 0 ] <> '$$$':
			return statement

def macro_lookahead( scope, aParameters, aMacros, defaultAttributeValue ):
	aParametersLookup = dict( ( name, value ) for name, value in aParameters )
	aPositional = []
	aNamed = {}
	aExtra = []
	for statement, type in lookahead_iter( scope, aMacros ):
		if type == '@':
			assert 2 <= len( statement ) <= 3
			name = tuple( statement[ 1 ] )
			if name in aParametersLookup:
				try:
					value = statement[ 2 ]
				except IndexError:
					value = aParametersLookup[ name ]
					if value is None:
						value = defaultAttributeValue

				aNamed[ name ] = value
			else:
				aExtra.append( statement )
		elif type == '$':
			assert len( statement ) == 2
			aPositional.append( statement[ 1 ] )
		else:
			aExtra.append( statement )

	# Assign remaining names to positional values.
	aPositionalNames = [ name for name, value in aParameters if name not in aNamed ]
	for ePositional in aPositional:
		name = aPositionalNames.pop( 0 )
		aNamed[ name ] = ePositional

	# Assign defaults to unspecified names.
	for name in aPositionalNames:
		value = aParametersLookup[ name ]
		# But, don't include name if no default was defined.
		if value is not None:
			aNamed[ name ] = value

	return aNamed, aExtra

def parse_macro( scope, aParameters, contents ):
	global xmlName, prefix, processingInstructionTarget

	aEvaluated = []
	for iStatement, ( statement, type ) in enumerate( scope_iter( scope ) ):
		#print 'Expanding:', statement, 'With parameters:', aParameters
		try:
			if type == '$#':
				assert 2 <= len( statement ) <= 3
				if len( statement ) == 3:
					prefixValue = evaluate_expression( statement[ 1 ], aParameters )
					prefixValue = prefix.parseString( prefixValue )[ 0 ]
					value = evaluate_expression( statement[ 2 ], aParameters )
					aEvaluated.append( [ '#', prefixValue, value ] )
				elif len( statement ) == 2:
					value = evaluate_expression( statement[ 1 ], aParameters )
					aEvaluated.append( [ '#', value ] )
			elif type == '$@':
				assert 2 <= len( statement ) <= 3
				attributeName = evaluate_expression( statement[ 1 ], aParameters )
				attributeName = xmlName.parseString( attributeName )[ 0 ]
				try:
					value = [ evaluate_expression( statement[ 2 ], aParameters ) ]
				except IndexError:
					value = []
				aEvaluated.append( [ '@', attributeName ] + value )
			elif type == '$<?':
				assert 2 <= len( statement ) <= 3
				target = evaluate_expression( statement[ 1 ], aParameters )
				target = processingInstructionTarget.parseString( target )[ 0 ]
				try:
					value = [ evaluate_expression( statement[ 2 ], aParameters ) ]
				except IndexError:
					value = []
				aEvaluated.append( [ '<?', target ] + value )
			elif type == '$"':
				assert len( statement ) == 2
				text = evaluate_expression( statement[ 1 ], aParameters )
				aEvaluated.append( [ '"', text ] )
			elif type == '$!':
				assert len( statement ) == 2
				text = evaluate_expression( statement[ 1 ], aParameters )
				aEvaluated.append( [ '!', text ] )
			elif type == '$<':
				assert len( statement ) >= 2
				elementName = evaluate_expression( statement[ 1 ], aParameters )
				elementName = xmlName.parseString( elementName )[ 0 ]
				aElementContents = parse_macro( statement[ 2 : ], aParameters, contents )
				aEvaluated.append( [ '<', elementName ] + aElementContents )
			elif type == '$$':
				assert len( statement ) == 1
				aEvaluated.extend( contents )
			elif type == '$$$':
				assert len( statement ) >= 2
				aElementContents = parse_macro( statement[ 2 : ], aParameters, contents )
				aEvaluated.append( list( statement[ : 2 ] ) + aElementContents )
			elif type == '<':
				assert len( statement ) >= 2
				aElementContents = parse_macro( statement[ 2 : ], aParameters, contents )
				aEvaluated.append( list( statement[ : 2 ] ) + aElementContents )
			else:
				aEvaluated.append( statement )
		except EvaluationError:
			pass

	#print 'Expanded Expanding:', aEvaluated
	return aEvaluated

class EvaluationError( pyparsing.ParseFatalException ):
	pass

def evaluate_expression( expression, aParameters ):
	#print 'Evaluating expression:', expression, 'With parameters:', aParameters
	value = ''
	for eAtom in expression:
		type = eAtom[ 0 ]
		if type == '"':
			value += eAtom[ 1 ]
		elif type == '@':
			name = eAtom [ 1 ]
			#print 'Lookup up name for expression:', name, aParameters
			try:
				value += aParameters[ tuple( name ) ]
			except KeyError:
				raise EvaluationError( 'Parameter %s not defined.' % name )
		else:
			raise ValueError( 'Unknown expression atom %r.' % eAton )

	return value

def parse_doctype( scope ):
	for statement, type in scope_iter( scope ):
		if type == '<!':
			assert len( statement ) == 3
			return statement[ 2 ]

def parse_preprocess( scope, aMacros, defaultAttributeValue ):
	for statement, type in scope_iter( scope ):
		if type == '?':
			assert len( statement ) >= 2
			command = statement[ 1 ]
			if command == 'load':
				assert len( statement ) == 3
				location = statement[ 2 ]
				from . import resolve
				resolved = resolve( location )
				assert isinstance( resolved, basestring )
				aNewMacros = load_macros( resolved, aMacros )
				aMacros.update( aNewMacros )
			elif command == 'default':
				assert len( statement ) == 3
				defaultAttributeValue = statement[ 2 ]
			elif command in ( 'attribute', 'element' ):
				assert len( statement ) >= 3
				name = statement[ 2 ]

				aParameters = []
				for aParameterParts in statement[ 3 ]:
					assert aParameterParts[ 0 ][ 0 ] == '@', 'Definition must be a variable.'
					parameterName = tuple( aParameterParts[ 0 ][ 1 ] )
					try:
						value = aParameterParts[ 1 ]
					except IndexError:
						value = None
					aParameters.append( ( parameterName, value ) )

				try:
					expansion = statement[ 4 : ]
				except IndexError:
					expansion = None

				if command == 'attribute':
					aMacros.add_attribute( name, aParameters, expansion )
				elif command == 'element':
					aMacros.add_element( name, aParameters, expansion )
				#print 'Macros:', aMacros
			else:
				raise ValueError( 'Unknown preprocessing command.' )

	return defaultAttributeValue

def parse_scope( scope, tree, aNamespaces, aMacros, defaultAttributeValue ):
	aCreatedInScope = []

	for statement, type in scope_iter( scope ):
		if type == '$$$':
			statement = expand_macro( statement, aMacros, defaultAttributeValue )
			type = statement[ 0 ]
			#print 'Expanded:', statement

		if type == '<':
			assert len( statement ) >= 2
			aElements, aAttributes, aFoundNamespaces = child_lookahead( statement, aMacros, defaultAttributeValue )
			aNewNamespaces = aNamespaces.copy( )
			aNewNamespaces.update( aFoundNamespaces )
			tag = xml_name( statement[ 1 ], aNewNamespaces )
			aAttributes = dict( ( xml_name( key, aNewNamespaces, True ), value ) for key, value in aAttributes.items( ) )
			tree.start( tag, aAttributes, nsmap = aNewNamespaces )
			ignored, defaultAttributeValue = parse_scope( aElements, tree, aNewNamespaces, aMacros, defaultAttributeValue )
			aCreatedInScope.append( tree.end( tag ) )
		elif type == '"':
			assert len( statement ) == 2
			tree.data( statement[ 1 ] )
		elif type == '!':
			assert len( statement ) == 2
			aCreatedInScope.append( tree.comment( statement[ 1 ] ) )
		elif type == '<?':
			assert len( statement ) == 3
			aCreatedInScope.append( tree.pi( statement[ 1 ], statement[ 2 ] ) )
		elif type == '?':
			defaultAttributeValue = parse_preprocess( [ statement ], aMacros, defaultAttributeValue )

	return aCreatedInScope, defaultAttributeValue

def child_lookahead( scope, aMacros, defaultAttributeValue ):
	aElements = []
	aAttributes = {}
	aNamespaces = {}
	for statement, type in lookahead_iter( scope, aMacros ):
		if type == '@':
			assert 2 <= len( statement ) <= 3
			name = statement[ 1 ]

			try:
				value = statement[ 2 ]
			except IndexError:
				value = defaultAttributeValue

			# Recognize literal namespace declarations.
			if name[ 0 ] == 'xmlns':
				aNamespaces[ name[ 1 ] ] = value
			else:
				aAttributes[ tuple( name ) ] = value
		elif type == '#':
			assert 1 <= len( statement ) <= 3
			if len( statement ) == 1:
				prefix = None
				value = u''
			elif len( statement ) == 2:
				prefix = None
				value = statement[ 1 ]
			elif len( statement ) == 3:
				prefix, value = statement[ 1 : ]
			aNamespaces[ prefix ] = value
		else:
			aElements.append( statement )

	return aElements, aAttributes, aNamespaces

def xml_name( aNameParts, aNamespaces, attribute = False ):
	if len( aNameParts ) == 1:
		name = aNameParts[ 0 ]
		# Attributes don't care about default namespace.
		if attribute:
			return name

		try:
			namespace = aNamespaces[ None ]
		except KeyError:
			return name
	else:
		prefix, name = aNameParts

		aDefaultNamespaces = {
			'xml' : 'http://www.w3.org/XML/1998/namespace',
			'xmlns' : 'http://www.w3.org/2000/xmlns',
			}

		try:
			namespace = aDefaultNamespaces[ prefix ]
		except KeyError:
			namespace = aNamespaces[ prefix ]

	if namespace:
		return '{%s}%s' % ( namespace, name )
	else:
		return name

def load_macros( compacted, macros = None ):
	# Create per call for thread safety.
	grammar = create_grammar( )
	parsed = grammar.parseString( compacted, True )

	#print 'Parsed:', parsed
	aMacros = Macros( ) if macros is None else copy.copy( macros )
	parse_preprocess( parsed, aMacros, '' )
	return aMacros

def expand( compacted, macros = None, namespaces = {} ):
	# Create per call for thread safety.
	grammar = create_grammar( )
	parsed = grammar.parseString( compacted, True )

	tree = etree.TreeBuilder( )

	#print 'Parsed:', parsed
	doctype = parse_doctype( parsed )
	aMacros = Macros( ) if macros is None else copy.copy( macros )

	aNamespaces = namespaces.copy( )
	# Remove default xml namespaces to prevent them being illegally
	# declared.
	for key in ( 'xml', 'xmlns' ):
		try:
			del aNamespaces[ key ]
		except KeyError:
			pass

	aCreated, defaultAttributeValue = parse_scope( parsed, tree, aNamespaces, aMacros, '' )
	lastElement = tree.close( )
	if len( aCreated ) == 1 and not doctype:
		return lastElement.getroottree( )
	else:
		aCreatedParts = [ etree.tostring( ePart ) for ePart in aCreated ]
		if doctype:
			doctypePart = '<!DOCTYPE %s>' % doctype
			aCreatedParts = [ doctypePart ] + aCreatedParts
		return etree.fromstring( ''.join( aCreatedParts ) ).getroottree( )
