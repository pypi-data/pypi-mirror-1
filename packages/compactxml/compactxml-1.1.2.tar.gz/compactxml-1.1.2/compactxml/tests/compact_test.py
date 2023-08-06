#!/usr/bin/python -tt

from __future__ import absolute_import

from lxml import etree

from compactxml import compact

def compacted( value, **kwargs ):
	print '\nInput to compact:\n', value
	result = compact( value, **kwargs )
	print '\nCompacted output:\n', result
	return result

def test_element( ):
	result = compacted( '<a/>' )
	assert result == '<a\n'

def test_nested( ):
	result = compacted( '<a><b><c/></b></a>' )
	assert result == '<a\n\t<b\n\t\t<c\n'

def test_attribute( ):
	result = compacted( '<a one="1"/>' )
	assert result == '<a\n\t@one=1\n'

def test_quoted_attribute( ):
	result = compacted( '<a one="1 2"/>' )
	assert result == '<a\n\t@one="1 2"\n'

def test_attribute_with_quotes( ):
	result = compacted( '<a one=\'"\'/>' )
	assert result == '<a\n\t@one=""""\n'

def test_attribute_with_newline( ):
	result = compacted( '''<a one="
"/>''' )
	assert result == '<a\n\t@one=" "\n'

def test_comment( ):
	result = compacted( '<a><!--Comment--></a>' )
	assert result == '<a\n\t!Comment\n'

def test_multiline_comment( ):
	result = compacted( '''<a><!--line 1
line 2
line 3
--></a>''' )

	assert result == '<a\n\t!line 1\n\t\\line 2\n\t\\line 3\n\t\\\n'


def test_pi( ):
	result = compacted( '<a><?target instruction?></a>' )
	assert result == '<a\n\t<?target instruction\n'

def test_multiline_pi( ):
	result = compacted( '''<a><?target line 1
line 2
line 3
?></a>''' )

	assert result == '<a\n\t<?target line 1\n\t\\line 2\n\t\\line 3\n\t\\\n'

def test_text( ):
	result = compacted( '<a>text</a>' )
	assert result == '<a\n\t"text\n'

def test_multiline_text( ):
	result = compacted( '''<a>line 1
line 2
line 3
</a>''' )

	assert result == '<a\n\t"line 1\n\t\\line 2\n\t\\line 3\n\t\\\n'

def test_whitespace( ):
	result = compacted( '<a>\n\t<ina/>\n</a>' )
	assert result == '<a\n\t"\n\t\\\t\n\t<ina\n\t"\n\t\\\n'

def test_strip_text( ):
	result = compacted( '<a>\n\t<ina/>\n</a>', stripText = True )
	assert result == '<a\n\t<ina\n'
