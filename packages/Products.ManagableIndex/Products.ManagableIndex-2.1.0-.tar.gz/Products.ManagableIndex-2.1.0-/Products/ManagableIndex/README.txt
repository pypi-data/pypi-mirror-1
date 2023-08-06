ManagableIndex
==============

``Products.ManagableIndex`` is a framework for the easy construction of
efficient, flexible, via the ZMI fully customizable indexes for Zope
2.11 (or above). It comes with a set of predefined indexes: Field,
Keyword, Path, Range, Word and SimpleText index. Usually, they
are more flexible and more efficient than the corresponding indexes from
the Zope core.

``Products.ManagableIndex`` uses ``dm.incrementalsearch`` when it is
installed. This can speed up queries by several orders of magnitude
when used together with ``Products.AdvancedQuery``.

You find more information in the ``doc`` subdirectory.

New
===

 * now with ``GenericSetup`` support.
