#!/usr/bin/python -tt

class Macros( object ):
	def __init__( self ):
		self.aAttributes = {}
		self.aElements = {}

	def __str__( self ):
		return '<Macros.macro instance with %d attributes and %d elements.>' % ( len( self.aAttributes ), len( self.aElements ) )

	def __repr__( self ):
		return '<Macros.macro instance %r attributes, %r elements>' % ( self.aAttributes, self.aElements )

	def __copy__( self ):
		macros = Macros( )
		macros.aAttributes = self.aAttributes.copy( )
		macros.aElements = self.aElements.copy( )
		return macros

	def __len__( self ):
		return len( self.aAttributes ) + len( self.aElements )

	def add_attribute( self, name, aParameters, expansion ):
		self.aAttributes[ name ] = ( aParameters, expansion )

	def add_element( self, name, aParameters, expansion ):
		self.aElements[ name ] = ( aParameters, expansion )

	def attribute( self, name ):
		return self.aAttributes[ name ]

	def element( self, name ):
		return self.aElements[ name ]

	def update( self, macrosToAdd ):
		self.aAttributes.update( macrosToAdd.aAttributes )
		self.aElements.update( macrosToAdd.aElements )
