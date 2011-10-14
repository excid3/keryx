#    Unwrapt - cross-platform package system emulator
#    Copyright (C) 2010 Chris Oliver <chris@excid3.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
import os
import sys

sys.path.append(os.path.dirname(__file__))

class DefinitionManager:
    """Definition Manager
    
    Loads the definitions from a folder and manages them
    """


    definitions = {}

    
    def __init__(self, folder):
        """Load all available definitions stored in folder"""
        
        #TODO: User path and variable expansions
        folder = os.path.abspath(folder)
        
        if not os.path.isdir(folder):
            logging.error("Unable to load plugins because '%s' is not a folder" % folder)
            return
        
        # Append the folder because we need straight access
        sys.path.append(folder)
        
        # Build list of folders in directory
        to_import = [f for f in os.listdir(folder) if not f.endswith(".pyc")]
                     
        # Do the actual importing
        for module in to_import:
            self.__initialize_def(module)
        
                        
    def __initialize_def(self, module):
        """Attempt to load the definition"""

        # Import works the same for py files and package modules so strip!
        if module.endswith(".py"):
            name = module [:3]
        else:
            name = module
        
        # Do the actual import
        __import__(name)
        definition = sys.modules[name]

        # Add the definition only if the class is available
        if hasattr(definition, definition.info["class"]):
            self.definitions[definition.info["name"]] = definition
            logging.info("Loaded %s" % name)
        

    def load(self, name, *args, **kwargs):
        """Creates a new instance of a definition
        name - name of the definition to create
        
        any other parameters passed will be sent to the __init__ function
        of the definition, including those passed by keyword
        """
        definition = self.definitions[name]
        return getattr(definition, definition.info["class"])(*args, **kwargs)
        
        
