.. Curtain documentation master file, created by
   sphinx-quickstart on Thu Jan 21 20:43:02 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Curtain's documentation!
=====================================

.. image:: logo.png
	:class: logo

**Curtain** is a simple, small **templating language**. Its characteristics
are:

- Supports just about the same features of :term:`TAL` and :term:`METAL`
  together with the `Zope internationalization extensions
  <http://wiki.zope.org/zope3/ZPTInternationalizationSupport>`_.
- Is **compiled** [#compiled]_.
- Allows **incremental production** of code through a :term:`SAX` event
  generator. In fact, Curtain could be better described as a SAX event
  processor, since SAX events are both its input and output.

If you want to use Curtain, you should go to the :ref:`installing` chapter.

Bugs
----

If you find a bug, we would love to hear about it so to fix it. You can find
our **bugtracking system** at `<http://sourceforge.net/apps/trac/curtain>`_. In
order to be helpful what you can do is, in order of increasing awesomeness:

- A *plain bug report*, writing a ticket which describe the problem.
- Attaching also a *minimal, working example* which shows the problem in
  question.
- Writing a *patch* against the latest SVN sources which solves the problem.
- Writing a *test case* which checks for regressions.

Blog
----

If you want to keep in touch about Curtain development, you can also give a
look at the `Curtain blog <http://sourceforge.net/apps/wordpress/curtain>`_,
and perhaps subscribe to `RSS feed
<http://sourceforge.net/apps/wordpress/curtain/feed/>`_.

Table of contents
-----------------

.. toctree::
    :maxdepth: 2

    installing
    programming_interface
    language_specification
    frameworks_integration
    glossary
    changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. rubric:: Footnotes

.. [#compiled] The template is compiled once to Python code, then to bytecode
    through Python's own mechanisms of code evaluation. There is not yet a
    support for saving the compiled version to a file for caching.
