.. highlight:: bash

.. _installing:

Installing Curtain
-------------------

Download
^^^^^^^^

The first thing you need is to **download the Curtain package**. You have the
following choices:

    - Get the **Python egg** from the `download page
      <http://sourceforge.net/projects/curtain/files>`_. In this case, you can
      simply install it by launching::

        $ easy_install <filename>.egg

      and nothing more is needed.

    - Get the **sources** from the `download page
      <http://sourceforge.net/projects/curtain/files>`_. After that, you can
      unpack them with::

        $ tar -xzvf <filename>.tar.gz

      To install Curtain from sources, see :ref:`installation`.

    - Get the **latest SVN sources**. To do it, you have to install the `subversion
      client <http://subversion.tigris.org>`_ and run::

        $ svn co https://curtain.svn.sourceforge.net/svnroot/curtain curtain

      To install Curtain from sources, see :ref:`installation`.

.. _installation:

Installation
^^^^^^^^^^^^

Once you have obtained Curtain sources either by downloading a source package
or via SVN, you can run this command to **install** the package on your
system::

    $ python setup.py install

Then you could run the **test suite** to be sure the installation was performed
correctly::

    $ python setup.py test

Anyway, use the :file:`README.txt` file you can found in the Curtain directory
for any other information.
