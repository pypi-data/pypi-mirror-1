.. highlight:: xml

.. _language-specification:

Language specification
----------------------

A Curtain template specifies a way of **transforming XML documents into XML
documents**, much like :term:`TAL` and XSLT do. A Curtain template is an XML
document with some more extra attributes and tags which specify how the
computation is made. Most of the values of the extra attributes contain Python
expressions.

The namespace of these Python expressions is initialized through the
:term:`environment`. An **environment** is a Python dictionary between string
(names) and arbitrary objects. When the execution begins, this mapping is
copied as-is in the namespace, which can then be modified by some instructions
(like :ref:`cdefn` or :ref:`cloop`). So, for example, if you have an
environment like ``{'name': u'Joe', 'surname': u'Black'}``, all the Python
expressions will see a variable ``name`` and a variable ``surname``
[#expression]_.

The `namespace <http://www.w3.org/TR/REC-xml-names/>`_ for Curtain
attributes and tags is ``http://curtain.sourceforge.net/NS/curtain``.  The
default **namespace** prefix used all through the documentation will be simply
``c``.

The value of the Curtain attributes is considered as the argument(s) of the
processing instruction. The value of attributes can be parsed in three
different ways, and all processing instructions use one of these (see the
glossary for their definition and how they work):

- :term:`simple attribute`
- :term:`single attribute`
- :term:`list attribute`

In the following section the various attributes are described.

Base language
^^^^^^^^^^^^^

Here we have the list of tags and attributes which contains the core of the language.

.. _ccont:

c:cont
""""""

:term:`simple attribute`

Replace the content of the tag on which this attribute is applied.  The
attribute value is evaluated as a Python expression, and the result replaces
the content of the attribute as character data. All previous content is
replaced by this character data. E.g., if you use this Curtain template::

    <?xml version="1.0"?>
    <root xmlns:c="http://curtain.sourceforge.net/NS/curtain"
          c:cont="u' '.join(words)">
        <removed-element/>
    </root>

With the environment ``{'words': [u'Hello', u'world']}``, the result is::

    <?xml version="1.0"?>
    <root>Hello world</root>

.. _cdefn:

c:defn
""""""

:term:`list attribute`

Adds new names (or temporarily overrides existing one's values) in the
namespace. For every piece of the attribute, this processing instruction
evaluates the second part as a Python expression and assign the result value to
the variable whose name is the first part of the expression. The new names will
be visible only for the expressions evaluated between the start and end of the
tag on which it's used the ``c:defn`` attribute and will shadow any previous
name (unshadowing it again when the tag is closed). E.g., if you use this
Curtain template::

    <?xml version="1.0"?>
    <root xmlns:c="http://curtain.sourceforge.net/NS/curtain">
        <before c:cont="x"/>
        <element c:defn="x u'newvalue'; y u'other value'">
            <inside c:cont="x"/>
            <inside c:cont="y"/>
        </element>
        <after c:cont="x"/>
    </root>

And call it with an environment of ``{'x': u'oldvalue'}``, the result will be::

    <?xml version="1.0"?>
    <root>
        <before>oldvalue</before>
        <element>
            <inside>newvalue</inside>
            <inside>other value</inside>
        </element>
        <after>oldvalue</after>
    </root>

.. _cloop:

c:loop
""""""

:term:`single attribute`

This attribute causes the subtree rooted at current tag to be produce many
times in the output. The Python expression which is in the second part of the
attribute value is evaluated and must return an iterable (list, generator,
tuple). This iterable is then looped over using the variable whose name is the
first part of the attribute value. E.g., if you evaluate the following
template::

    <?xml version="1.0"?>
    <ul>
        <li c:loop="name all_names">The name is <c:c c:cont="name"/>!</li>
    </ul>

Over the environment ``{'all_names': [u'Joe', u'Mark', u'Albert']}``, the
result is [#formatted]_::

    <?xml version="1.0"?>
    <ul>
        <li c:loop="name all_names">The name is Joe!</li>
        <li c:loop="name all_names">The name is Mark!</li>
        <li c:loop="name all_names">The name is Albert!</li>
    </ul>

.. _ccond:

c:cond
""""""

:term:`simple attribute`

The attribute value is evaluated as a Python expression, converted to ``bool``,
and if it evaluates to a ``False`` value, the tag and all its children are
removed from the output.  E.g., if you have a template like::

    <?xml version="1.0"?>
    <root>
        <paragraph c:cond="username">Hello <c:c c:cont="username"/>!</paragraph>
        <paragraph c:cond="not username">Welcome visitor!</paragraph>
    </root>

And an environment of ``{'username': u'Bobby'}``, the result will be::

    <?xml version="1.0"?>
    <root>
        <paragraph>Hello Bobby!</paragraph>
    </root>

Whereas with an environment of ``{'username': None}`` you would have::

    <?xml version="1.0"?>
    <root>
        <paragraph>Welcome visitor!</paragraph>
    </root>

.. _cattr:

c:attr
""""""

:term:`list attribute`

Whereas :ref:`ccont` defines the content of a tag, :ref:`cattr` defines the
attributes. For each piece of the attribute value, the first part is
interpreted as the attribute name, and the second part as a Python expression
which, once converted to unicode, produces the attribute value. E.g., this
template::

    <?xml version="1.0"?>
    <table c:defn="zebraclasses [u'even', u'odd']">
        <th>
            <td>value</td><td>square</td>
        </th>
        <tr c:loop="i range(10)"
            c:attr="class zebraclasses[i%2]; id u'row_%d' % i">
            <td c:cont="i"/><td c:cont="i*i"/>
        </tr>
    </table>

With an empty environment produces the following XML [#formatted]_::

    <?xml version="1.0"?>
    <table>
        <th>
            <td>value</td><td>square</td>
        </th>
        <tr id="row_0"> <td>0</td><td>0</td>  </tr>
        <tr id="row_1"> <td>1</td><td>1</td>  </tr>
        <tr id="row_2"> <td>2</td><td>4</td>  </tr>
        <tr id="row_3"> <td>3</td><td>9</td>  </tr>
        <tr id="row_4"> <td>4</td><td>16</td> </tr>
        <tr id="row_5"> <td>5</td><td>25</td> </tr>
        <tr id="row_6"> <td>6</td><td>36</td> </tr>
        <tr id="row_7"> <td>7</td><td>49</td> </tr>
        <tr id="row_8"> <td>8</td><td>64</td> </tr>
        <tr id="row_9"> <td>9</td><td>81</td> </tr>
    </table>

.. _cskip:

c:skip
""""""

:term:`simple attribute`

The skip processing instruction is substantially the same of :ref:`ccond`, but
removes just the tag itself in case the condition evaluates to ``False``, not
all the subtree. So, with a template like::

    <?xml version="1.0"?>
    <ul>
        <li c:loop="s sections">
            <a c:attr="href s" c:skip="s == current">
                section <em c:cont="s"/>
            </a>
        </li>
    </ul>

And an environment like ``{'sections': ['home', 'blog', 'forum'], 'current':
'blog'}``, you would get this XML [#formatted]_::

    <?xml version="1.0"?>
    <ul>
        <li><a href="home">section <em>home</em></a></li>
        <li><a href="blog">section <em>blog</em></a></li>
        <li>               section <em>forum</em>   </li>
    </ul>

.. _cc:

c:c
"""

This is the only tag of Curtain. This tag is simply omitted, and is useful
just for attaching other attributes to it so to apply transformations to parts
of text instead of just the content of whole tags. E.g., this template::

    <?xml version="1.0"?>
    <paragraph>Welcome <c:c c:cont="username"/>!</paragraph>

With the environment ``{'username': u'Joe'}``, produce this XML::

    <?xml version="1.0"?>
    <paragraph>Welcome Joe!</paragraph>

Macro system
^^^^^^^^^^^^

Most of the time, and especially when developing non-trivial websites, you have
a common structure for many web pages where some parts of them, called
:term:`slots <slot>`, change according to the section. A tipical example of
changing slots would be the central and left column of a web page, whereas the
header and footer of it remains the same all throughout the site.

:term:`Macros <macro>` are a convenient mechanism to implement the automatisms needed
for such a task. A macro is just a template like any other which marks some of
its subtrees as :term:`slots <slot>`. Any other template which has a reference to
this template object through its environment can then use the macro specifying
how to fill some or all of the slots.

.. _cslot:

c:slot
""""""

:term:`simple attribute`

This attribute mark the subtree of the element where it is applied as a slot,
and the value of the attribute is the symbolic name through which the slot is
referred to. This means that when a slot substitution will be performed, this
element and all its children will be removed and replaced by the value given.
If no slot substitution is performed, the tree rooted at this element will be
kept.

.. _cuse:

c:use
"""""

:term:`simple attribute`

The attribute value is evaluated as a Python expression, and must return a
template. Through this tag you declared that the element and all its content
are ignored (except for the subtrees whose roots are tagged with the
:ref:`cfill` attribute) and replaced by the content of the macro. The slots of
the macro can be filled thanks to the :ref:`cfill` attribute.

.. _cfill:

c:fill
""""""

:term:`simple attribute`

This attribute is valid only in an element which is a descendant of some
element tagged with a :ref:`cuse` attribute. It specifies that this element and
all its children will replace the slot of the macro in use with the same name
as the value of the attribute :ref:`cfill`.

Example
"""""""

The use of the :ref:`cuse`, :ref:`cslot` and :ref:`cfill` tags it's much
clearer through an example. Let's say you have ``macro.ct``, which is this
(macro) template::

    <?xml version="1.0"?>
    <page>
        <header>Welcome to The Page!</header>
        <column><c:c c:slot="leftcolumn">left column</c:c></column>
        <column><c:c c:slot="body"/></column>
        <footer>Copyright 2010 Mattia Belletti</footer>
    </page>

And also this other template, ``home.ct``::

    <?xml version="1.0"?>
    <c:c c:use="macro">
        <paragraph c:fill="leftcolumn">Index</paragraph>
        <paragraph c:fill="body">Welcome to our site.</paragraph>
    </c:c>

Then you could wire together this code:

.. code-block:: python

    from xml.sax.saxutils import XMLGenerator
    from curtain import Template
    macro = Template('macro.ct')
    home = Template('home.ct')
    xml_generator = XMLGenerator('home.xml')
    home(xml_generator, env = {'macro': macro})

Which would produce this XML::

    <?xml version="1.0"?>
    <page>
        <header>Welcome to The Page!</header>
        <column><paragraph>Index</paragraph></column>
        <column><paragraph>Welcome to our site.</paragraph></column>
        <footer>Copyright 2010 Mattia Belletti</footer>
    </page>

But then, if you have another page, e.g. ``credits.ct``::

    <?xml version="1.0"?>
    <c:c c:use="macro">
        <paragraph c:fill="body">The authors are Tom, Jerry and
        Mark.</paragraph>
    </c:c>

You can just add a couple more lines of code:

.. code-block:: python

    credits = Template('credits.ct')
    xml_generator = XMLGenerator('credits.xml')
    credits(xml_generator, env = {'macro': macro})

And this would produce the ``credits.xml``::

    <?xml version="1.0"?>
    <page>
        <header>Welcome to The Page!</header>
        <column>left column</column>
        <column><paragraph>The authors are Tom, Jerry and
        Mark.</paragraph></column>
        <footer>Copyright 2010 Mattia Belletti</footer>
    </page>

(Notice that the ``leftcolumn`` slot was not specified, so it was left
unchanged from the master macro)

Internationalization
^^^^^^^^^^^^^^^^^^^^

When an application must be used by a number of different people coming from
various cultures (and thus often different languages), the development has a
difficult additional task. The main problem regards the internationalization of
the application - that is, the task of engineering and factoring the various
aspects of the application input/output which can change according to the
user's culture: strings, dates, lengths, ...

Curtain tackles the problem of internationalization just for what regards the
translation of text. To do so, it uses Zope's i18n machinery, which is mostly
based on the `ITranslationDomain
<http://docs.zope.org/zope3/Interface/zope.i18n.interfaces.ITranslationDomain/index.html>`_
interface and the `translate
<http://docs.zope.org/zope3/Code/zope/i18n/translate/index.html>`_ method.
Curtain offers some tags to mark text which must be translated, and then the
correct ``ITranslationDomain`` is queried for the translation of the message
itself.

.. _ctranslate:

c:translate
"""""""""""

:term:`simple attribute`

The value of this attribute is ignored. The tag just marks the fact that the
characters contents of this element need to be translated. E.g., if we write
this template::

    <?xml version="1.0"?>
    <root>
        <paragraph c:translate="">Welcome to our site!</paragraph>
    </root>

We are expressing the fact that the string ``u'Welcome to our site!'`` must be
given to the translation service, which will return the translated string to
put in there. To know how the translation service is queried, see
:ref:`translationprocedure`.

The situation gets more complicated when the data inside the translation unit
is not just characters data, but there are also some tags. In this case, see
:ref:`cname`.

.. _cname:

c:name
""""""

:term:`simple attribute`

The :ref:`cname` attribute resolves the problem of having tags in the middle of
the translation unit's characters data. E.g.::

    <?xml version="1.0"?>
    <body c:translate="">
        Welcome back, <a c:attr="href context/userlink" c:cont="context/username"/>!
    </body>

Here, the translation unit has some tag in the middle, but it would be good to
translate the message as a whole, without splitting it in two parts and
translating the two parts separately. Also because we could have more complex
cases, like::

    <?xml version="1.0"?>
    <body c:translate="">
        I am sure that <em c:cont="context/username"/> was in here the <em
        c:cont="context/date"/> last time.
    </body>

In this case, according to the language, it could happen that the position of
the two tags gets inverted. How can we manage all these cases? The solution is
to put a name on the tags which are in the middle of a translation unit::

    <?xml version="1.0"?>
    <body c:translate="">
        I am sure that <em c:name="username" c:cont="context/username"/> was in
        here the <em c:name="date" c:cont="context/date"/>.
    </body>

If you do that, the message passed to the translation system will be ``u'I am
sure that ${username} was in here the ${date}'``. Translations are required to
return back these special tags (called *interpolations*), and they will be
substituted by the corresponding XML trees. Translation units can also be
nested this way::

    <?xml version="1.0"?>
    <body c:translate="">
        Welcome back, <span class="user" c:name="usertag" c:translate="">Mr.
        <a c:name="username" c:attr="href context/userlink"/></span>.
    </block>

In this case, we will ask the translation service a translation for the string
``u'Mr. ${username}'``, and then another one for ``u'Welcome back,
${usertag}'``.

.. _cdomain:

c:domain
""""""""

:term:`simple attribute`

The value of this attribute sets the current :term:`translation domain`. This
translation domain will be used until the end of the element with this
attribute, where the old translation domain will be restored.

.. _translationprocedure:

Translation procedure
"""""""""""""""""""""

Every time there's a message to translate, be it a plain message or containing
some interpolation, the Zope's i18n machinery is queried through the `translate
<http://docs.zope.org/zope3/Code/zope/i18n/translate/index.html>`_ method. The
arguments are:

- ``msgid``: the string to translate, containing interpolations or not.
- ``domain``: the last domain set by a :ref:`cdomain` attribute, or ``None`` if
  no translation domain has been set (which is something to avoid).
- ``context``: the translation context as passed from the template. This is
  tipically a "request" object of the web framework in use which is then
  translated (adapted) to obtain a language.

As you can notice, no value is given to ``mapping``, so tipically no
substitution of the mapping values is performed. This is then internally
executed by the Curtain system, and the translation system has not to worry
about it.

.. rubric:: Footnotes

.. [#expression] Since only Python *expressions* are allowed and no Python
                 *statements*, the only way to change a variable's value is by
                 "overriding" it through some processing instruction like
                 :ref:`cdefn`.
.. [#formatted] The XML has been formatted to improve legibility.
