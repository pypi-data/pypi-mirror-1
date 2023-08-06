Appendix
========

.. _using_with_zope:

Using Chameleon with Zope
-------------------------

As part of the effort to use Chameleon with Zope 2 and 3 (including applications such as the content management system `Plone <http://www.plone.org>`_), several packages have been developed:

:mod:`z3c.pt`
    Drop-in replacement of Zope Page Templates including full framework support.

:mod:`z3c.ptcompat`
    Tools to transition a project to Chameleon.

:mod:`five.pt`
    Extension that allows using Chameleon with Zope 2

:mod:`cmf.pt`
    Extension that allows using Chameleon with the Zope 2 content management framework CMF

.. _reflimpl:

Notable Differences from TAL 1.4
--------------------------------

The :mod:`chameleon.zpt` compiler is largely compatible with the targeted dialects. The TAL implementation is based on the `1.4 language specification <http://wiki.zope.org/ZPT/TALSpecification14>`_.


#. The default expression type is Python.

#. Tuple unpacking is supported in a variable definition statement::

      ``tal:define="(a, b, c) [1, 2, 3]"``

#. If attribute-access fails, a dictionary lookup is attempted::

      ``obj.key``

   can be used instead of ``obj['key']``, so long as `key` is not an attribute of `obj`.

#. The ``tal:on-error`` statement is not implemented.

