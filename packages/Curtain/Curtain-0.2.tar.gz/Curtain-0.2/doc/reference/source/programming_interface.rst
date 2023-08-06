.. _programming-interface:

Programming interface
---------------------

A tipical usage of Curtain is as simple as that::

    from xml.saxutils import XMLGenerator
    from curtain import Template
    template = Template(file_source = '/path/to/template.ct')
    xml_generator = XMLGenerator('/path/to/output.xml')
    template(xml_generator, env = {'project': u'test'})

So, it all boils down to loading (and thus compile) a template file,
instantiating an XML generator, and calling the template.

:mod:`curtain` -- Main curtain module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. module:: curtain
    :synopsis: Compilation and execution of templates.
.. moduleauthor:: Mattia Belletti

.. class:: Template(str_source = None, file_source = None, auto_reload = False)

    A compiled Curtain template.

    .. method:: __init__(str_source = None, file_source = None, auto_reload = False)

        Either ``str_source`` or ``file_source`` must be given, but not both.
        ``str_source`` is a ``str`` object containing the XML template (the
        parser will manage the encoding using the tipical XML `encoding
        declaration <http://www.w3.org/TR/REC-xml/#NT-EncodingDecl>`_ and/or
        `autodetection of characters encoding
        <http://www.w3.org/TR/REC-xml/#sec-guessing>`_), whereas
        ``file_source`` can be either a ``str`` containing the path to an XML
        file with the template, or an open file-like object where data can be
        read from (again, the encoding is computed using the previous
        mechanisms).

        ``auto_reload`` can be ``True`` only if file_source is given and is a
        path. In this case, the template will manage the auto-reloading of the
        template file if it is changed. This can cause quite a heavy
        performance hit, so it should be considered just as a development
        utility, and kept to off in production environments.

    .. method:: __call__(xml_generator, env, translation_context = None, location = None)

        Execute the compiled template. Execution of the template implies that a
        sequence of XML SAX events are sent the ``xml_generator`` object, which
        must implement the `xml.sax.handlers.ContentHandler
        <http://docs.python.org/library/xml.sax.handler.html#contenthandler-objects>`_
        interface. ``env`` is the environment in which the template is
        executed. See the :ref:`language specification
        <language-specification>` for more informations about that.
        ``translation_context`` is the context passed to the `translate
        <http://docs.zope.org/zope3/Code/zope/i18n/translate/index.html>`_
        method. See :ref:`translationprocedure`. ``location`` is a
        :class:`Location` object instance which will track the position in the
        source template file while execution is performed, so to have
        informations about where the computation has stopped in case of errors.

.. class:: Location()

    An object containing a location in an XML file.

    .. attribute:: current

        A couple ``(line, column)`` which gives the current position of the
        location object.
