#!/usr/bin/python -tt

from __future__ import absolute_import

from lxml import etree

import compactxml

def expand( compacted, **kwargs ):
	print '\nInput to expand:\n', compacted
	result = compactxml.expand( compacted, **kwargs )
	print '\nExpanded output:\n', etree.tostring( result )
	return result

def test_element( ):
	result = expand( '<a' )
	assert result.getroot( ).tag == 'a'

def test_nested_element( ):
	result = expand( '''<a
	<b
	<c
	<d
		<ind
	<e''' )

	assert result.find( 'b' ) is not None
	assert result.find( 'd/ind' ) is not None
	assert result.find( 'e' ) is not None

def test_multiple_nested_element( ):
	result = expand( '''
<a
	<b
		<c
			<d
				<e
	<b2
		<c2
	<b3
''' )

	assert result.find( 'b' ) is not None
	assert result.find( 'b/c' ) is not None
	assert result.find( 'b/c/d' ) is not None
	assert result.find( 'b/c/d/e' ) is not None
	assert result.find( 'b2' ) is not None
	assert result.find( 'b2/c2' ) is not None
	assert result.find( 'b3' ) is not None

def test_element_following_multiline_text( ):
	result = expand( '''
<a
	"
	\\
	<b
		"In b.
''' )

	assert result.find( '/b' ).text == 'In b.'

def test_leading_whitespace( ):
	result = expand( '''


<a''')

	assert result.getroot( ).tag == 'a'

def test_trailing_whitespace( ):
	result = expand( '''<a


''')

	assert result.getroot( ).tag == 'a'

def test_element_whitespace( ):
	result = expand( '''

<a


	<b


''')

	assert result.find( 'b' ) is not None

def test_incorrect_indent_whitespace( ):
	result = expand( '''

<a
			
	
	<b

			
		
	

''')

	assert result.find( 'b' ) is not None

def test_tabs_roundtrip( ):
	result = expand( '''
<a
	"
	\\	
	<b
	"
	\\
''')

	assert result.getroot( ).text == '\n\t'
	assert result.find( 'b' ).tail == '\n'

def test_inline_attribute( ):
	result = expand( '''
<a @one=1
''' )

	assert result.getroot( ).attrib[ 'one' ] == '1'

def test_attribute( ):
	result = expand( '''
<a
	@one=1
''' )

	assert result.getroot( ).attrib[ 'one' ] == '1'

def test_interleaved_attribute( ):
	result = expand( '''
<a
	@one=1
	<b
		<inb
	@two=2
''' )

	assert result.getroot( ).attrib[ 'one' ] == '1'
	assert result.getroot( ).attrib[ 'two' ] == '2'

def test_quoted_attribute( ):
	result = expand( '''
<a @double="double" @single='single' @with_spaces="with spaces"
''' )

	assert result.getroot( ).attrib[ 'double' ] == 'double'
	assert result.getroot( ).attrib[ 'single' ] == 'single'
	assert result.getroot( ).attrib[ 'with_spaces' ] == 'with spaces'

def test_attribute_whitespace( ):
	result = expand( '''
<a @ inline = inline 
	@ standalone = standalone 
	@ quoted = 'quoted' 
''' )

	assert result.getroot( ).attrib[ 'inline' ] == 'inline'
	assert result.getroot( ).attrib[ 'standalone' ] == 'standalone'
	assert result.getroot( ).attrib[ 'quoted' ] == 'quoted'

def test_default_attribute( ):
	result = expand( '''
<a @default @alsodefault @value=value
''' )

	assert result.getroot( ).attrib[ 'default' ] == ''
	assert result.getroot( ).attrib[ 'alsodefault' ] == ''
	assert result.getroot( ).attrib[ 'value' ] == 'value'

def test_set_default_attribute( ):
	result = expand( '''
?default true
<a @default
''' )

	assert result.getroot( ).attrib[ 'default' ] == 'true'

def test_xmlns_attribute_namespace( ):
	result = expand( '''
<a
	@xmlns:test="namespace"
	<test:in-namespace
''' )

	assert result.find( '{namespace}in-namespace' ) is not None

def test_namespace( ):
	result = expand( '''
<a
	#default
	#one=one
	#two=two
	<b
	<one:b
	<two:b
''' )

	assert result.getroot( ).tag == '{default}a'
	assert result.find( '{default}b' ) is not None
	assert result.find( '{one}b' ) is not None
	assert result.find( '{two}b' ) is not None

def test_inline_namespace( ):
	result = expand( '''
<a #default #one=one #two=two
	<b
	<one:b
	<two:b
''' )

	assert result.getroot( ).tag == '{default}a'
	assert result.find( '{default}b' ) is not None
	assert result.find( '{one}b' ) is not None
	assert result.find( '{two}b' ) is not None

def test_override_namespace( ):
	result = expand( '''
<a #default #one=one
	<b
		#otherdefault
	<one:b
		#one=otherone
''' )

	assert result.getroot( ).tag == '{default}a'
	assert result.find( '{otherdefault}b' ) is not None
	assert result.find( '{otherone}b' ) is not None

def test_attribute_namespace( ):
	result = expand( '''
<a #default #one=one @first=1 @one:first=one
''' )

	assert result.getroot( ).attrib[ 'first' ] == '1'
	assert result.getroot( ).attrib[ '{one}first' ] == 'one'

def test_default_declared_namespace( ):
	result = expand( '''
<a
	@xml:id=value
''' )

	assert result.getroot( ).attrib[ '{http://www.w3.org/XML/1998/namespace}id' ] == 'value'

def test_declared_namespace( ):
	result = expand( '''
<test:a
''', namespaces = { 'test' : 'namespace' } )

	assert result.getroot( ).tag == '{namespace}a'

def test_remove_default_declared_namespace( ):
	result = expand( '''
<a
''', namespaces = { 'xmlns' : 'fake' } )

	assert result.getroot( ).tag == 'a'

def test_text( ):
	result = expand( '''
<a
	"Hello, 
	"world.
	<b
		"inb
	"afterb
''' )

	assert result.getroot( ).text == 'Hello, world.'
	assert result.find( 'b' ).text == 'inb'
	assert result.find( 'b' ).tail == 'afterb'

def test_multiline_text( ):
	result = expand( '''
<a
	"One
	\Two
	\Three
''' )

	assert result.getroot( ).text == 'One\nTwo\nThree'

def test_text_whitespace( ):
	result = expand( '''
<a
	" One 
	\ Two 
	\ Three 
''' )

	assert result.getroot( ).text == ' One \n Two \n Three '

def test_blank_text( ):
	result = expand( '''
<a
	"
''' )

	assert result.getroot( ).text == ''

def test_comment( ):
	result = expand( '''
<a
	!comment
''' )

	assert str( result.getroot( )[ 0 ] ) == '<!--comment-->'

def test_comment_whitespace( ):
	result = expand( '''
<a
	! comment 
	\ and space 
''' )

	assert str( result.getroot( )[ 0 ] ) == '<!-- comment \n and space -->'

def test_blank_comment( ):
	result = expand( '''
<a
	!
''' )

	assert str( result.getroot( )[ 0 ] ) == '<!---->'

def test_processing_instruction( ):
	result = expand( '''
<a
	<?target instruction
''' )

	assert str( result.getroot( )[ 0 ] ) == '<?target instruction?>'

def test_processing_instruction_whitespace( ):
	result = expand( '''
<a
	<?target instruction
	\ followed by 
	\ spaces.
''' )

	assert str( result.getroot( )[ 0 ] ) == '<?target instruction\n followed by \n spaces.?>'

def test_indentation( ):
	result = expand( '''
<a
	<
<b
	<
<c
	>
	>
''' )

	assert result.find( 'b' ) is not None
	assert result.find( 'b/c' ) is not None

def test_doctype( ):
	result = expand( '''
<!DOCTYPE a SYSTEM "id"
<a
''' )

	assert result.docinfo.doctype == '<!DOCTYPE a SYSTEM "id">'

def test_toplevel( ):
	result = expand( '''
?default "default"
<!DOCTYPE a SYSTEM "id"
!one
<?pi target first
<a
!two
<?pi target second
''' )

	assert result.docinfo.doctype == '<!DOCTYPE a SYSTEM "id">'
	assert 'one' in etree.tostring( result )
	assert 'two' in etree.tostring( result )
	assert 'first' in etree.tostring( result )
	assert 'second' in etree.tostring( result )

# Attribute group tests.

def test_group( ):
	result = expand( '''
?attribute test
	#
	#default
	#prefix=testns
	@default
	@name=value
<root
	@@test
	<prefix:element
''' )

	assert result.getroot( ).attrib[ 'default' ] == ''
	assert result.getroot( ).attrib[ 'name' ] == 'value'
	assert result.getroot( ).tag == '{default}root'
	assert result.find( '{testns}element' ) is not None

def test_group_override( ):
	result = expand( '''
?attribute test
	@first=one
	@second=two
<root
	@first=1
	@@test
	@second=2
''' )

	assert result.getroot( ).attrib[ 'first' ] == 'one', 'Should be overridden by group.'
	assert result.getroot( ).attrib[ 'second' ] == '2', 'Should override group.'

def test_group_default( ):
	result = expand( '''
?default before
?attribute test
	@default
?default after
<root
	@@test
''' )

	assert result.getroot( ).attrib[ 'default' ] == 'after'

def test_group_macro( ):
	result = expand( '''
?attribute test
	@name=value
?element test
	<test
		@@test
test
''' )

	assert result.getroot( ).attrib[ 'name' ] == 'value'

def test_group_namespaced( ):
	result = expand( '''
?attribute namespace:test
	@name=value
<root
	@@namespace:test
''' )

	assert result.getroot( ).attrib[ 'name' ] == 'value'

# Macro tests.

def test_macro( ):
	result = expand( '''
?element test
	<test
test
''' )

	assert result.getroot( ).tag == 'test'

def test_macro_toplevel( ):
	result = expand( '''
?element simple
	<simple
?element nested
	<nested
?element macro
	nested
?element variable @one
	$<@one
<root
	simple
	macro
	variable @one=variable
''' )

	assert result.find( 'simple' ) is not None
	assert result.find( 'nested' ) is not None
	assert result.find( 'variable' ) is not None


def test_macro_parameters( ):
	result = expand( '''
?element test @one @two=value
	<test
test
''' )

	assert result.getroot( ).tag == 'test'

def test_macro_positional( ):
	result = expand( '''
?element test @one @two
	<test
		$@ "first" = @one
		$@ "second" = @two
test 1 2
''' )

	assert result.getroot( ).tag == 'test'
	assert result.getroot( ).attrib[ 'first' ] == '1'
	assert result.getroot( ).attrib[ 'second' ] == '2'

def test_macro_named( ):
	result = expand( '''
?element test @one @two
	<test
		$@ "first" = @one
		$@ "second" = @two
test @two=2 @one=1
''' )

	assert result.getroot( ).tag == 'test'
	assert result.getroot( ).attrib[ 'first' ] == '1'
	assert result.getroot( ).attrib[ 'second' ] == '2'

def test_macro_parameter_defaults( ):
	result = expand( '''
?element test @one @two=default
	<test
		$@ "first" = @one
		$@ "second" = @two
test
''' )

	assert result.getroot( ).tag == 'test'
	assert result.getroot( ).attrib[ 'second' ] == 'default'

	try:
		result.getroot( ).attrib[ 'first' ]
	except KeyError:
		pass
	else:
		assert False, 'one attribute should not exist.'

def test_macro_parameter_extra( ):
	result = expand( '''
?element test
	<test
		$$
test @third="3"
''' )

	assert result.getroot( ).attrib[ 'third' ] == '3'

def test_macro_parameter_evaluate( ):
	result = expand( '''
?element test @one
	<test
		$" "before" + @one + "after" + @one + @one + "repeated"
test 1
''' )

	assert result.getroot( ).text == 'before1after11repeated'

def test_macro_statements( ):
	result = expand( '''
?element test @name @value
	<tests
		$@ @name = @value
		$# @name = @value
		$" @value
		$! @value
		$<? @name @value
		$< @name
			<child
test name value
''' )

	assert len( result.getroot( ) ) == 3
	assert result.getroot( ).attrib[ 'name' ] == 'value'
	assert result.find( 'name' ) is not None
	assert result.find( 'name/child' ) is not None
	assert result.getroot( ).text == 'value'
	assert str( result.getroot( )[ 0 ] ) == '<!--value-->'
	assert str( result.getroot( )[ 1 ] ) == '<?name value?>'

def test_nested_macro_expansion( ):
	result = expand( '''
?element two
	<two
?element one
	two
one
''' )

	assert result.getroot( ).tag == 'two'

def test_macro_namespaced( ):
	result = expand( '''
?element namespace:test
	<test
namespace:test
''' )

	assert result.getroot( ).tag == 'test'
