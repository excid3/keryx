# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import gettext
from gettext import gettext as _
gettext.textdomain('keryx')

import gtk
import logging
logger = logging.getLogger('keryx')

from keryx_lib import Window
from keryx.AboutKeryxDialog import AboutKeryxDialog
from keryx.PreferencesKeryxDialog import PreferencesKeryxDialog

# See keryx_lib.Window.py for more details about how this class works
class KeryxWindow(Window):
    __gtype_name__ = "KeryxWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(KeryxWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutKeryxDialog
        self.PreferencesDialog = PreferencesKeryxDialog

        # Code for other initialization actions should be added here.

