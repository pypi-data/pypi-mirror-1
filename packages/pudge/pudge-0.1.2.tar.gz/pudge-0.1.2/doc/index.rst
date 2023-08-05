=====
Pudge
=====

---------------------------
Python Documentation System
---------------------------

Overview
--------

Pudge is a documentation system for Python_ projects.

- Generate documentation for Python packages, modules, classes, functions, 
  and methods.
- Module and Class index hierarchies 
  (`hierarchy example <module-pudge-index.html>`_)
- Support for `Restructured Text`_ in docstrings.
- Easily apply common free documentation licenses (`GNU`_, `CC`_).
- Syntax colored source HTML generation with anchors for line numbers 
  (`source example <./pudge/scanner.py.html>`_).
- Generated reference documents link to source for all modules,
  classes, functions, and methods.
- Basic `Restructured Text`_ document templating (brings external documents
  into the flow of generated pages).
- Support for HTML 4.01 or XHTML 1.0 output.
- Basic `Trac`_ integration (adds Trac project links to navigational
  elements).
- Uses a combination of runtime inspection and Python source code scanning.
- Extensible and customizable using `kid templates`_.
- Optional use of Restructured Text "..code-block:: Python" (an other languages supported by SilverCity). Enabled by installing SilverCity.

.. _Restructured Text: http://docutils.sourceforge.net/rst.html
.. _Python: http://www.python.org
.. _Trac: http://projects.edgewall.com/trac/
.. _kid templates: http://kid.lesscode.org/
.. _GNU: http://www.gnu.org/copyleft/fdl.html
.. _CC: http://creativecommons.org/license/meet-the-licenses

Status
------

Pudge is currently under development.  It's largely maintained by its
users; changes only happen if you make them happen.

Pudge is usually used through buildutils_, with configuration stored
in a ``setup.cfg`` file, and documentation generated with ``python
setup.py pudge`` (however, there is also a ``pudge`` script).

If you'd like to take an early peek, you can grab the latest sources
using `subversion`_::

  svn co http://lesscode.org/svn/pudge/trunk pudge

Pudge news, articles, and ramblings are posted to the `lesscode.org
blog`_ tagged with `pudge`_.

.. _subversion: http://subversion.tigris.org/ 

Get Involved
~~~~~~~~~~~~

Join the `Pudge mailing list`_.

.. _pudge: http://lesscode.org/blog/category/pudge/
.. _buildutils: http://buildutils.lesscode.org/
.. _lesscode.org blog: http://lesscode.org/blog/category/pudge/
.. _Pudge mailing list: http://lesscode.org/mailman/listinfo/pudge
