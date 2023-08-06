===========
Compact XML
===========

--------
Overview
--------

Compact XML is an alternative syntax for representing XML files. It uses
indentation to indicate nesting to give a python like feel, and has a macro
system to shorten common XML constructs. It is intended for element based XML
files, especially those where the elements share a common structure, such as
gizmo service definition files.

------------
Content Type
------------

The compact XML content type used within gizmo is
``application/x.gizmo.compactxml``. Additional suffixes of any type are
allowed, and specify what the file extension of the content type of the XML
will be after being expanded. For instance, XSLT data would use the
``application/x.gizmo.compactxml.xslt`` content type.

The file extensions used are looked up as usual for file types in the main
gizmo configuration file.

------
Values
------

There are two kinds of values in compact XML. Single line values, as used by
attributes and namespaces, and multi-line values, as used for text values,
comments, and others. Additionally, there is a special case used only in
macros.

Single Line Value
-----------------
Single line values can not contain newlines, and as such are only used in
attribute values where newlines are ignored by XML.As long as the value
contains no whitespace, the value can be specified without quotes. However, if
whitespace is present, quote the value with ``"`` or ``'`` quote marks. To
escape quotes, double them within the quoted string, like so ``"Quoth the
raven, ""Nevermore."""``

Multi-line Value
----------------
Multi-line values extend to the end of the line, and never need to be quoted.
The only special case is to escape newlines, which is done by continuing the
line at the same indent level, and prefixing with a ``\``.

Macro Value
-----------
Macro values are a special kind of value only used in macro expansion
statements, those that start with ``$``. They consist of a combination of
`single line values`_ and expansion parameters, separated by ``+`` signs.
Expansion parameters are simply an ``@`` followed by the parameter name. A
sample value would look like ``"before " + @value + " after"`` and would
expand to ``before middle after`` if the ``@value`` parameter was ``middle``.

------
Syntax
------

The compact XML syntax is line oriented, with nesting indicated by
indentation.

Compact XML uses a prefix based syntax to indicate node type. The available
nodes are as follows:

Elements
--------
XML elements are prefixed with ``<``, followed by the name of the element.
Elements with a namespace are specified as normal for xml with the prefix
followed by a colon, then the remainder of the name. Nodes contained within an
element are indicated by indenting the contained nodes. Both namespace and
attribute declarations can be made as child elements or inline.

Only elements may have child nodes.

For example, here are three nested elements::

	<one
		<two
			<three

Which correspond to the following XML::

	<one><two><three/></two></one>

Notice the lack of whitespace in the converted XML.

Element Macros
--------------
Element macros must first be defined by an ``?element`` macro. Once defined,
they are included by name alone, with no prefix. See the macros_ section for
details.

Attributes
----------
XML attributes are prefixed with ``@`` and must appear as the child of an
element or inline in an element definition. They consist of a name, with
optional namespace prefix, followed by an ``=`` sign, and then a `single line
value`_.

If no value is given, the attribute will have the current default attribute
value.

For example, here is a single element with an attribute value::

	<one
		@name=value

Or, in alternate inline format::

	<one @name=value

Which correspond to the following XML::

	<one name="value"/>

Attribute Groups
----------------
Attribute groups must first be defined by an ``?attribute`` macro. Once
defined, they are included with the ``@@`` prefix followed by the macro name.
See the macros_ section for details.

Namespaces
----------
XML namespace definitions are prefixed with ``#`` and must appear as the child
of an element or inline in an element definition. Namespaces may be declared
with a prefix similarly to attributes, with the prefix name followed by an
``=`` sign then the namespace URI as a `single line value`_. However, default
namespaces are declared by specifying only the namespace URI.

URIs will also have to be quoted if they contain ``=`` signs.

For example, here is an element declared in a namespace::

	<test:a
		#test=http://www.testuri.com

Or, in alternative inline format::

	<test:a #test=http://www.testuri.com

Which corresponds to the following XML::

	<test:a xmlns:test="http://www.testuri.com"/>

Text
----
Text is prefixed with ``"`` followed by a `multi-line value`_.

For example, here is a multi-line text value::

	<a
		"Line one.
		\Line two.
		\Line three.

Which corresponds to the following XML::

	<a>Line one.
	Line two.
	Line three.</a>

Comments
--------
Comments are prefixed with ``!`` followed by a `multi-line value`_.

For example, here is a multi-line comment::

	!Line one.
	\Line two.
	\Line three.

Which corresponds to the following XML::

	<!--Line one.
	Line two.
	Line three.-->

Processing Instructions
-----------------------
Processing instructions are prefixed with ``<?`` followed by a target as
specified by XML, and then a `multi-line value`_.

For example, here is a simple processing instruction::

	<? target instruction

Which corresponds to the following XML::

	<?target instruction?>

Document Type Definitions
-------------------------
Document type definitions are prefixed with ``<!`` followed by ``DOCTYPE`` and
a `multi-line value`_ specifying the rest of the document type as required by
XML.

Document type definition can only be specified at the top level of the
document, and only one is allowed per document.

Due to limitations in the lxml library used, when compacting XML to compact
XML format, inline DTD defintions in DOCTYPE declarations are lost.

For example, the standard XHTML doctype declaration looks like this::

	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	\ "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"

Which corresponds to the following XML::

	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

Indentation
-----------
The indentation level can be reset for highly nested documents by using a
``<`` alone to reset the indentation to the first column, and a ``>`` alone to
reset the indentation to the previous level.

For example, here is an element nested inside of another, using reset
indentation::

	<a
		<
	<b
		>

Which corresponds to the following XML::

	<a><b/></a>

------
Macros
------

Compact XML contains a macro syntax for defining commonly used elements and
groups of attributes. Macros must be defined at the top level of a document,
before any nodes (including document type definitions).

Attribute Groups
----------------
Attribute groups are defined with the ``?attribute`` macro declaration,
followed by a macro name. The declaration may contain any number of attribute
(``@`` statements) or namespace (``#`` statements) declarations.

When an attribute group is included by a ``@@`` statement, the defined
attributes and namespaces are inserted at that location.

For example, an attribute group definition would look like this::

	?attribute test
		@one=1
		@two=2
		@three=3

And would be included as part of an element like so::

	<a
		@@test

Resulting in the following XML::

	<a one="1" two="2" three="3"/>

Element Macros
--------------
Element macros are used to declare a common form for an XML element. It allows
for shortening common structures, as well as declaring attributes by
declaration position as well as by name.

Element macros are defined using the ``?element`` macro declaration, followed
by a macro name and a list of parameters and default values. The first child
of the declaration must be an element or an equivalent (such as a reference to
a previously defined element macro).

All the standard node types work as normal within a macro definition and are
simply inserted literally. However, there are also special macro versions of
the standard node types which have a leading ``$``, including ``$<``, ``$@``,
``$#``, ``$"``, ``$!``, and ``$<?``. These have the same format as the
standard node types, except all values are specified as a `macro value`_
instead of the expected single or multi-line value. The macro expansion
element node, ``$<``, is a special case in that it does not accept inline
attribute or namespace declarations, those must be specified on their own
line.

There is one more special macro node type, which is the ``$$`` statement. This
declares where the contents (all child nodes) of the macro will be inserted.
If this is omitted, the child nodes of the macro will be silently ignored.

For example, a simple element macro definition with a pair of attributes would
look like this::

	?element test @one @two
		<test
			$@ one = @one
			$@ two = @two
			$$

It could be called using positional parameters like so::

	test 1 2

Or named parameters::

	test @one=1 @two=2

Or even named parameters on separate lines::

	test
		@one=1
		@two=2

All of which would create the following XML::

	<test one="1" two="2"/>

Attribute Defaults
------------------
The ``?default`` macro command specifies the default value to use for
attributes without values, and can be specified anywhere within the document.
It takes a `single line value`_ as its only value.

The default value used if nothing has been set is the empty string ``''``.

For example, this set of default declarations::

	<a
		@empty
		?default value
		@default

Would result in the following XML::

	<a empty="" default="value"/>
