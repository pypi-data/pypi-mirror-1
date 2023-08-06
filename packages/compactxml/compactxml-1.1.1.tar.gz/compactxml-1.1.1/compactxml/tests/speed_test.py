#!/usr/bin/python -tt

from __future__ import absolute_import

import time

from lxml import etree

import compactxml

def expand( compacted, **kwargs ):
	print '\nInput to expand:\n', compacted
	result = compactxml.expand( compacted, **kwargs )
	print '\nExpanded output:\n', etree.tostring( result )
	return result

def test_speed( ):
	startTime = time.time( )

	result = expand( '''
?element serialize
	<serialize
		$$
?element include @ignored
	<include
		$$
?element inline
	<inline
		$$
?element request
	<request
		$$
?element source @ignored
	<source
		$$
serialize
	#xsd="http://www.w3.org/2001/XMLSchema"
	#py="http://codespeak.net/lxml/objectify/pytype"
	#rng="http://relaxng.org/ns/structure/1.0"
	#soap="http://schemas.xmlsoap.org/soap/envelope/"
	#gtest="http://www.lt-systems.com/gizmo-test.xsd"
	#env="http://www.w3.org/2003/05/soap-envelope"
	#gconf="http://www.lt-systems.com/gizmo-configuration.xsd"
	#gtype="http://www.lt-systems.com/gizmo-type.xsd"
	#xsi="http://www.w3.org/2001/XMLSchema-instance"
	#xhtml="http://www.w3.org/1999/xhtml"
	#xsl="http://www.w3.org/1999/XSL/Transform"
	#gizmo="http://www.lt-systems.com/gizmo.xsd"
	include local:../maintenance.cgizmo
		<query
			<statement
				"DELETE FROM DocumentCategories;
	include local:../maintenance.cgizmo
		inline
			request
				include local:esi_document_types.cgizmo
			source application/x.gizmo.xslt+xml
				<

<xsl:stylesheet @version=1.0
	<xsl:output @method=xml @indent=no
	<xsl:template @match=/
		<query
			<statement
				"INSERT INTO DocumentCategories VALUES ( %s, %s );
			<xsl:apply-templates @select=readu/record
	<xsl:template @match=record
		<parameters
			<parameter
				<xsl:value-of @select="value[ @name = '@ID' ]/text()"
			<parameter
				<xsl:value-of @select="value[ @name = 'DESCRIPTION' ]/text()"

				>
''' )

	assert time.time( ) - startTime < 1.0
