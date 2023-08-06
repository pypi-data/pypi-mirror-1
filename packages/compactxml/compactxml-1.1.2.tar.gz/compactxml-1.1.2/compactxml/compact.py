#!/usr/bin/python -tt

from __future__ import absolute_import

from lxml import etree

def compact( xmlFile, macros = None, namespaces = {}, stripText = False ):
	cIndent = 0
	aNamespaceStack = []
	aNewNamespaceDeclarations = []
	compacted = ''

	def indent( ):
		return cIndent * '\t'

	def quote( value ):
		if ' ' in value or '\t' in value or '"' in value:
			return '"%s"' % value.replace( '"', '""' )
		else:
			return value

	def text_lines( text, prefix = '"' ):
		if stripText:
			text = text.strip( )

		lines = ''
		if text:
			textPrefix = prefix
			for eLine in text.split( '\n' ):
				if stripText:
					eLine = eLine.strip( )

				lines += '%s%s%s\n' % ( indent( ), textPrefix, eLine )
				textPrefix = '\\'

		return lines

	def prefixed_name( name ):
		qname = etree.QName( name )
		if qname.namespace:
			for prefix, namespace in aNamespaceStack[ : : -1 ]:
				if namespace == qname.namespace:
					break
			else:
				raise KeyError( 'Namespace not found.' )

			if prefix:
				return '%s:%s' % ( prefix, qname.localname )

		return qname.localname

	events = ( 'start', 'end', 'start-ns', 'end-ns', 'comment', 'pi' )
	for action, element in etree.iterparse( xmlFile, events ):
		if action == 'start':
			#TODO: Use default macros when possible.
			compacted += '%s<%s\n' % ( indent( ), prefixed_name( element.tag ) )
			cIndent += 1
			for namespaceDeclaration in aNewNamespaceDeclarations:
				compacted += indent( ) + namespaceDeclaration
			aNewNamespaceDeclarations = []
			for name, value in element.attrib.items( ):
				compacted += '%s@%s=%s\n' % ( indent( ), prefixed_name( name ), quote( value ) )
			if element.text:
				compacted += text_lines( element.text )
		elif action == 'end':
			cIndent -= 1
			if element.tail:
				compacted += text_lines( element.tail )
			# Memory optimization.
			element.clear( )
		elif action == 'start-ns':
			#TODO: Avoid creating namespace declaration when in default namespaces.
			prefix, namespace = element
			if prefix:
				aNewNamespaceDeclarations.append( '#%s=%s\n' % ( prefix, quote( namespace ) ) )
			else:
				aNewNamespaceDeclarations.append( '#%s\n' % quote( namespace ) )
			aNamespaceStack.append( ( prefix, namespace ) )
		elif action == 'end-ns':
			aNamespaceStack.pop( )
		elif action == 'comment':
			compacted += text_lines( element.text, '!' )
		elif action == 'pi':
			compacted += text_lines( '%s %s' % ( element.target, element.text ), '<?' )
		else:
			raise ValueError( 'Unknown parse action %s.' % action )

	return compacted
