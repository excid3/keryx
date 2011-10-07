# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import os
import platform
import shutil
import traceback

import gettext
from gettext import gettext as _
gettext.textdomain('keryx')

import gtk
import logging
logger = logging.getLogger('keryx')

from keryx_lib import Window
from keryx.AboutKeryxDialog import AboutKeryxDialog
from keryx.PreferencesKeryxDialog import PreferencesKeryxDialog
from keryx.MessageDialogs import *

EXT = ".keryx"
SUPPORTED = ["Ubuntu"]
PATHS = [os.path.abspath("data"),
         os.path.abspath(os.path.expanduser("~/keryx"))]

# See keryx_lib.Window.py for more details about how this class works
class KeryxWindow(Window):
    __gtype_name__ = "KeryxWindow"

    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(KeryxWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutKeryxDialog
        self.PreferencesDialog = PreferencesKeryxDialog

        # Code for other initialization actions should be added here.
        self._initialize_home()


    def _open_profile(self, profile_path):
        print profile_path


    def on_manage_button_clicked(self, widgt, data=None):
        model, row_iter = self.ui.computers_treeview.get_selection().get_selected()
        if row_iter:
            profile_path = model.get_value(row_iter, 1)
            self._open_profile(profile_path)


    def on_browse_button_clicked(self, widget, data=None):
        dialog = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        dialog.set_current_folder(self._find_path())

        keryx_filter = gtk.FileFilter()
        keryx_filter.set_name("Keryx profiles")
        keryx_filter.add_pattern("*.keryx")

        dialog.add_filter(keryx_filter)

        response = dialog.run()
        profile_path = dialog.get_filename() if response == gtk.RESPONSE_OK else None
        dialog.destroy()

        if profile_path:
            self._open_profile(profile_path)


    def on_add_profile_button_clicked(self, widget, data=None):
        # Find our output directory
        path_used = self._find_path()

        # Make sure the output directory is writable
        if not path_used:
            error_dialog(self, "Make sure one of the following paths are writable: %s" % ", ".join(PATHS))
            return

        # Retrieve the profile name
        profile_name = self.ui.profile_name_entry.get_text()
        profile_dir = os.path.join(path_used, "profiles", profile_name)
        profile_path = os.path.join(profile_dir, "%s.keryx" % profile_name)

        # Create the output directory if necessary
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)

        if os.path.exists(profile_path):
            error_dialog(self, "A profile with this name already exists!")
            return

        try:
            self._write_keryx_file(profile_path)
            self._copy_sources(profile_dir)

            # Alert that patient user the good news, we've got a project written
            # for them! :D
            info_dialog(self, "Your computer has been added successfully!\n" \
                    "Take this profile to an online machine to download" \
                    "packages.\n\n" \
                    "You can find the profile here:\n%s" % profile_dir)
        except Exception, e:
            traceback.print_exc()
            error_dialog(self, "There was a problem creating your profile: \n" \
                    "%s" % e)


    def _write_keryx_file(self, profile_path):
        # Write out the profile attributes
        # - Distro (Ubuntu)
        # - Version (11.04)
        # - Architecture (x86_64/i386)
        f = open(profile_path, "wb")
        f.write("\n".join(platform.uname()[0:1]))
        f.close()

    def _copy_sources(self, profile_dir):
        # Copy the sources
        shutil.copy("/etc/apt/sources.list", profile_dir)
        shutil.copytree("/etc/apt/sources.list.d", os.path.join(profile_dir,
            "sources.list.d"))

    def _copy_status(self, profile_dir):
        # Copy dpkg status
        shutil.copy("/var/lib/dpkg/status", profile_dir)


    def _initialize_home(self):
        """Initialize anything in the home screen"""
        self.ui.profile_name_entry.set_text(platform.uname()[1])
        self._load_profiles()

        # Hide the add computer expander if running an unsupported OS
        if platform.uname()[0] != "Linux" or not platform.dist()[0] in SUPPORTED:
            self.ui.add_expander.set_expanded(False)


    def _load_profiles(self):
        """Append all the .keryx profiles found into the list"""
        for path in PATHS:
            for (path, dirs, files) in os.walk(os.path.join(path, "profiles")):
                for f in files:
                    if f.endswith(EXT):
                        self.ui.computers_liststore.append((f.strip(EXT),os.path.join(path,f)))


    def _find_path(self):
        """Finds a path to write the profile to"""
        for path in PATHS:
            if os.access(os.path.abspath(path), os.W_OK):
                return path
        return None
