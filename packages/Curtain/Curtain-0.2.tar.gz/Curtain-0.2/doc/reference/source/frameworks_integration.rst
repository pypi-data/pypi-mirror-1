.. _frameworks-integration:

Frameworks integration
----------------------

repoze.bfg
^^^^^^^^^^

.. highlight:: xml

To enable the usage of Curtain in your `repoze.bfg <http://bfg.repoze.org/>`_
project, it's enough to add the following line in your :file:`configure.zcml`::

    <include package="curtain.bfg" />
