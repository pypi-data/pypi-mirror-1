.. _index:

=============
chameleon.zpt
=============

This package provides a no-frills implementation of the Zope Page Templates (ZPT) language. It's the place to start if you want to use ZPT outside of a complete Zope 2 or 3 environment.

.. note:: If you're looking to use Chameleon in a complete Zope 2 or 3 environment, the `z3c.pt <http://pypi.python.org/pypi/z3c.pt>`_ package is a drop-in replacement to the default implementation. See :ref:`using_with_zope`.

Zope Page Templates (ZPT) is a system which can generate HTML and XML.
ZPT is formed by the *Template Attribute Language* (*TAL*), the
*Expression Syntax* (*TALES*), *Intertionalization*  (*I18N*) and the *Macro Expansion Template Attribute Language* (*METAL*).

Users Guide
===========

.. toctree::
   :maxdepth: 2

   narr/intro
   narr/appendix

Language Reference
==================

This reference is split into parts that correspond to each of the main language features.

.. toctree::
   :maxdepth: 2

   narr/tal
   narr/tales
   narr/metal
   narr/i18n

API Documentation
=================

.. toctree::
   :maxdepth: 2

   api

Support and Development
=======================

To report bugs, use the `bug tracker <https://bugs.launchpad.net/chameleon.zpt>`_.

If you've got questions that aren't answered by this documentation,
please contact the `mailing-list
<http://groups.google.com/group/z3c_pt>`_.

Browse and check out tagged and trunk versions of :mod:`chameleon.zpt`
via the `Repoze Subversion repository <http://svn.repoze.org/chameleon.zpt/>`_.  To
check out the trunk via Subversion, use this command::

  svn co svn://svn.repoze.org/chameleon.zpt/trunk chameleon.zpt

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

