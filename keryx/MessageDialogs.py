# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2010 Chris Oliver <chris@excid3.com>
#                    mac9416 <mac9416@keryxproject.org>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

"""We have here several simple dialogs for convenience."""

import gtk
    
def dialog(parent, text, title, buttons, gtk_message):
    """
        A generic dialog box
    """
    md = gtk.MessageDialog(parent,
                           gtk.DIALOG_DESTROY_WITH_PARENT,
                           gtk_message,
                           buttons,
                           text)
    if title:
        md.set_title(title)
        
    result = md.run()
    md.destroy()
    
    return result

def error_dialog(parent, text, title=None, buttons=gtk.BUTTONS_OK):
    """
        An error dialog box
        
        Returns True if OK response
    """
    result = dialog(parent, text, title, buttons, gtk.MESSAGE_ERROR)
    return result == gtk.RESPONSE_OK

def info_dialog(parent, text, title=None, buttons=gtk.BUTTONS_OK):
    """
        An information dialog box
        
        Returns True if OK response
    """
    result = dialog(parent, text, title, buttons, gtk.MESSAGE_INFO)
    return result == gtk.RESPONSE_OK


def question_dialog(parent, text, title=None, buttons=gtk.BUTTONS_YES_NO):
    """
        A Yes/No question dialog box
        
        Returns True if Yes response
    """
    result = dialog(parent, text, title, buttons, gtk.MESSAGE_QUESTION)
    return result == gtk.RESPONSE_YES


def warning_dialog(parent, text, title=None, buttons=gtk.BUTTONS_OK):
    """
        A warning dialog box
        
        Returns True if OK response
    """
    result = dialog(parent, text, title, buttons, gtk.MESSAGE_WARNING)
    return result == gtk.RESPONSE_OK
