This package patches Zope's ``ZTUtils`` to improve it.

Currently, ``ZTUtils.Zope.complex_marshal`` is replaced by a variant
that correctly handles unicode and tuples. In addition, empty lists
(and tuples) are retained. Tuples are marshalled as lists. This
patch makes "make_query" and "make_hidden_input" more reliable.
