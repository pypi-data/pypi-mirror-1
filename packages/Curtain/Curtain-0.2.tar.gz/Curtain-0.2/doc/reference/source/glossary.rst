Glossary
========

.. glossary::

    TAL
        The `Template Attribute Language
        <http://wiki.zope.org/ZPT/TALSpecification14>`_ is an attribute
        language used to create dynamic templates. It allows elements of a
        document to be replaced, repeated, or omitted.
    METAL
        The `Macro Expansion Template
        <http://wiki.zope.org/ZPT/METALSpecification11>`_ Attribute Language is
        an attribute language for structured macro preprocessing. It can be
        used in conjunction with or independently of :term:`TAL`, TALES and
        ZPT.
    SAX
        The `Simple API for XML <http://www.saxproject.org/>`_ is an interface
        for the sequential processing of XML documents, in constrast with DOM.
        Python implements this specification in the `xml.sax` package and
        subpackages.
    environment
        The namespace in which a courtain template is evaluated; it is
        represented as a python dictionary between names and arbitrary objects.
    macro
        A macro is a template with some subtrees marked as :term:`slot`. When
        the macro is used, these slots can be replaced with other content.
    slot
        A slot is a "hole" in a macro, which can be replaced with different
        content by whoever calls the macro.
    translation domain
        The translation domain is a string which tells the kind of translations
        to find for words, so to avoid ambiguities and separate the message
        catalogs for different applications or different parts of the same
        application. E.g., a tipical example of the ambiguity would be the word
        "Sun", which can mean the star if we are in the "astronomical"
        translation domain, the company if we are in the "commercial" one, or
        the day if we are in the "calendar" one. On the other hand, if
        different applications use different translation domains, there will be
        no risk of clash between names and translations used, keeping the
        development separated.
    simple attribute
        One of the way of parsing an attribute; in this case the value of the
        attribute is the argument of the processing instruction.
    single attribute
        One of the way of parsing an attribute; in this case the value of the
        attribute is split at the first space found; the two pieces are called
        "first part" and "second part" of the attribute.
    list attribute
        One of the way of parsing an attribute; in this case the value of the
        attribute is split at every semicolon, then all the pieces are parsed
        as if they were :term:`single attributes <single attribute>`. The
        various elements of the resulting list are the "pieces" of the
        attribute, each one composed of a "first part" and a "second part".
