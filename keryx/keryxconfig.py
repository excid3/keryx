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

# THIS IS Keryx CONFIGURATION FILE
# YOU CAN PUT THERE SOME GLOBAL VALUE
# Do not touch unless you know what you're doing.
# you're warned :)

__all__ = [
    'project_path_not_found',
    'get_data_file',
    'get_data_path',
    ]

# Where your project will look for your data (for instance, images and ui
# files). By default, this is ../data, relative your trunk layout
__keryx_data_directory__ = '../data/'
__license__ = 'GPL-3'

import ConfigParser
import os

import gettext
from gettext import gettext as _
gettext.textdomain('keryx')

class project_path_not_found(Exception):
    """Raised when we can't find the project directory."""


def get_data_file(*path_segments):
    """Get the full path to a data file.

    Returns the path to a file underneath the data directory (as defined by
    `get_data_path`). Equivalent to os.path.join(get_data_path(),
    *path_segments).
    """
    return os.path.join(get_data_path(), *path_segments)


def get_data_path():
    """Retrieve keryx data path

    This path is by default <keryx_lib_path>/../data/ in trunk
    and /usr/share/keryx in an installed version but this path
    is specified at installation time.
    """

    # Get pathname absolute or relative.
    path = os.path.join(
        os.path.dirname(__file__), __keryx_data_directory__)

    abs_data_path = os.path.abspath(path)
    if not os.path.exists(abs_data_path):
        raise project_path_not_found

    return abs_data_path
    
class Config:
    section = "keryx"
    defaults = [("data", get_data_path()), 
                ("projects", os.path.join(get_data_path(), "projects")), 
                ("downloads", os.path.join(get_data_path(), "downloads")),
                ("proxy", "False"),
                ("proxy_url", "http://localhost"),
                ("proxy_port", "3182"),
                ("proxy_username", ""),
                ("proxy_password", ""),
                ]

    def __init__(self, config_file=None):
        self._config = ConfigParser.ConfigParser()

        config_path = config_file or os.path.join(get_data_path(), "keryx.conf")
        if os.path.exists(config_path):
            self._load_config(config_path)
        else:
            self._set_defaults()
        self.config_file = config_path
        
        projects_path = os.path.join(get_data_path(), "projects")
        
        if not os.path.exists(projects_path):
            os.mkdir(projects_path)    
    
    def get_filename(self):
        return self.config_file
    
    def set(self, key, value):
        self._config.set(self.section, key, str(value))
    
    def get(self, key):
        """Retrieve a configuration key"""
        try:
            return self._config.get(self.section, key)
        except:
            self._set_defaults()
            return self._config.get(self.section, key)
            
    def _set_defaults(self):
        try:
            self._config.add_section("keryx")
        except:
            pass
            
        # Initialize defaults if key isn't available
        for key, val in self.defaults:
            if not self._config.has_option(self.section, key):
                self._config.set(self.section, key, val)
        
    def _load_config(self, filename):
        """Parse a configuration file"""
        self._config.read(filename)
        
    def save(self):
        print "saving config"
        with open(self.config_file, "wb") as configfile:
            self._config.write(configfile)

