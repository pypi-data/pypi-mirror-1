===================================
About collective.monkeypatcherpanel
===================================

Introduction
============

collective.monkeypatcherpanel is the Zope 2 companion of Martin Aspeli's
`collective.monkeypatcher
<http://pypi.python.org/pypi/collective.monkeypatcher>`_ component.

It just add a ZMI control panel that shows what monkey patches have been applied
in case you cannot see the logs or grep through the ZCML of your Zope
instance. Open the control panel of your Zope instance, then the "Monkey
Patches" control panel, et voilà.

Requirements
============

collective.monkeypatcherpanel has been developed and tested with Zope 2.10 and
Zope 2.11. It may run on Zope 2.9 but this is untested and not supported unless
you provide a patch that keeps the tests smiling.

Of course, we require `collective.monkeypatcher`. If you installed
`collective.monkeypatcherpanel` with easy_install or a zc.buildout, you're done.

License
=======

Copyright (c) 2009 Ingeniweb SAS

This software is subject to the provisions of the GNU General Public License,
Version 2.0 (GPL). A copy of the GPL should accompany this distribution. THIS
SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE
DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE,
MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

The full text of the GPL v2 license is `here
<http://www.gnu.org/licenses/gpl-2.0.txt>`_.

Credits
=======

* `Gilles Lenfant <gilles.lenfant@ingeniweb.com>`_

The icon has been stolen to the `Tango Desktop Project
<http://tango.freedesktop.org/Tango_Desktop_Project>`_.
