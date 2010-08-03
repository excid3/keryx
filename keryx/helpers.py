# -*- coding: utf-8 -*-
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

"""Helpers for an Ubuntu application."""

__all__ = [
    'make_window',
    ]

import os
import gtk

from keryx.keryxconfig import get_data_file

import gettext
from gettext import gettext as _
gettext.textdomain('keryx')

def get_builder(builder_file_name):
    """Return a fully-instantiated gtk.Builder instance from specified ui 
    file
    
    :param builder_file_name: The name of the builder file, without extension.
        Assumed to be in the 'ui' directory under the data path.
    """
    # Look for the ui file that describes the user interface.
    ui_filename = get_data_file('ui', '%s.ui' % (builder_file_name,))
    if not os.path.exists(ui_filename):
        ui_filename = None

    builder = gtk.Builder()
    builder.set_translation_domain('keryx')
    builder.add_from_file(ui_filename)
    return builder
    
def create_closeable_tab(notebook, title, widget):
    """
        Create a notebook tab
    """
    
    hbox = gtk.HBox(False, 0)
    label = gtk.Label(title)
    hbox.pack_start(label)
    
    close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
    image_w, image_h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
    
    btn = gtk.Button()
    btn.set_relief(gtk.RELIEF_NONE)
    btn.set_focus_on_click(False)
    btn.add(close_image)
    hbox.pack_start(btn, False, False)
    
    # Reduce the size of the button
    style = gtk.RcStyle()
    style.xthickness = 0
    style.ythickness = 0
    btn.modify_style(style)
    
    hbox.show_all()
    
    create_tab(notebook, hbox, widget)
    btn.connect("clicked", on_close_tab_button_clicked, notebook, widget)

def create_tab(notebook, title, widget):
    """
        Create a tab with title (any gtk.Widget) as title and widget as the
        primary widget inside the tab
    """
    
    if isinstance(title, str): 
        label = gtk.Label(title)
    else:
        label = title
        
    notebook.insert_page(widget, label)

def on_close_tab_button_clicked(sender, notebook, widget):
    """
        Tab close button clicked event, removes the tab
    """

    pagenum = notebook.page_num(widget)
    notebook.remove_page(pagenum)
    
