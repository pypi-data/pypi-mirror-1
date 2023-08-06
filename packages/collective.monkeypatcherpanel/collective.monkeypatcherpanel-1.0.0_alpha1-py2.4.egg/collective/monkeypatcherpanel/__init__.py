# -*- coding: utf-8 -*-
# $Id: __init__.py 84178 2009-04-13 18:02:35Z glenfant $
"""collective.monkeypatcherpanel"""

import Globals

from controlpanel import ControlPanel

def initialize(context):
    """Zope 2 registration"""

    # FIXME: somehow dirty way to get the control panel. Something cleaner available around?
    zope_control_panel = context._ProductContext__app.Control_Panel
    cp_id = ControlPanel.id
    if cp_id not in zope_control_panel.objectIds():
        control_panel = ControlPanel()
        zope_control_panel._setObject(cp_id, control_panel)

    # Setting the icon (whaaaa, noisy, but can't "context.registerClass" for this)
    from OFS.misc_ import misc_, Misc_
    icon = Misc_('collective.monkeypatcherpanel',
                 {'icon.png': Globals.ImageFile('zmi/face-monkey.png', globals())})
    setattr(misc_, 'collective.monkeypatcherpanel', icon)
    return
