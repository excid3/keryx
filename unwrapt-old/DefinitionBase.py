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

import os

#from sqlalchemy import create_engine
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import sessionmaker


#Base = declarative_base()


def callback(func):
    """
        Our decorator for giving on_<function name> callbacks to definitions
        
        The DefinitionBase functions will do their work, and then the real
        defintion will do its work. The return values from the definition will
        be the results returned.
    """
    
    def callback_func(*args, **kwargs):
        # Call the base function
        func(*args, **kwargs)
        
        # Call callback if available
        name = "on_%s" % func.__name__
        if hasattr(args[0], name):
            return getattr(args[0], name)(*args[1:], **kwargs)

    return callback_func
        

class DefinitionBase:
    """
        DefinitionBase
        
        This is the base class for all definitions and provides some default
        functionality as well as providing callbacks for definitions to
        implement their code. This helps to make sure that functionality is not
        overridden when implementing a new definition.
    """
    
    download_directory = "downloads"
    
    
    @callback
    def __init__(self):
        """
            __init__()
              
            For example:
              
            client = loader.new_instance("apt")
        """
        
        #self.database = database
        #engine = create_engine("sqlite:///%s" % database)
        #Base.metadata.create_all(engine)
        
        #Session = sessionmaker(bind=engine)
        #self.session = Session()
	
        pass
	

    #def __del__(self):
    #    self.session.commit()
    #    self.session.close()

    
    @callback
    def set_download_directory(self, directory):
        """
            set_download_directory(directory)
            
            - directory is the location of the 
        """
        #FIXME: that docstring.
        
        self.download_directory = os.path.abspath(os.path.expanduser(directory))


    @callback
    def set_architecture(self, architecture):
        """
            set_architecture(architecture)
            
            - architecture is the platform architecture of the machine.
              Supported types are amd64, armel, i386, ia64, powerpc, sparc
               
            For example:
               
            client.set_architecture("amd64")
        """
          
        self.architecture = architecture
        
        
    @callback
    def set_proxy(self, proxy, username=None, password=None):
        """
            set_proxy(proxies, [username, [password]])
            - proxy is a dictionary of the protocols and their url's.
             
            - The last two parameters for proxy authentication and are 
              optional. If omitted, no proxy authentication will be attempted.
               
            For example:
               
            proxies = {'http': 'http://www.someproxy.com:3128'}
            client.set_proxy(proxies, "default", "admin")

        """

        self.proxy = {"proxy": proxy,
                      "user": username,
                      "pass": password}
    
    
    @callback
    def set_repositories(self, repositories):
        """
            set_repositories(repositories)
            
            - repositories is a list of "deb url dist section" lines taken
              straight from the machine's sources.list file.
              
            For example:download_directory 
              
            f = open("/etc/apt/sources.list", "rb")
            client.set_repositories(f.readlines())
            f.close()
        """
        
        self.repositories = repositories
        

    @callback
    def set_status(self, status):
        """
            set_status(status)
            
            - status is the filename containing the package statuses
            
            Sets the package statuses from the offline machine
            
            For example:
            
            client.set_status("/var/lib/dpkg/status")
        """
        
        pass


    @callback        
    def update(self, reporthook=None, directory=None, download=True):
        """
            update(reporthook=None, directory=None, download=True)
            
            - reporthook is a function name that will be called to report the 
              progress of files as they are being downloaded. If omitted, the
              function will print out progress into the console.
        
            - directory is the location to store and read the files from
            
            - download is a boolean to determine if files are downloaded or not
              This is useful for machines that are offline and packages are
              going to be marked and downloaded later on.
        
            Updates the list of available packages
        
            For example:
            
            client.update()
        """
        
        pass

        
    @callback
    def get_available_package_names(self):
        """
            get_available_package_names()
            
            Returns a list of package names
            
            For example:
            
            names = client.get_available_package_names()
        """
        
        pass
        

    @callback
    def get_latest_binary(self, package):
        """
            get_latest_binary(package)
            
            - package is the name of the package. 
            
            This function will return the newest version of the package 
            available.
              
            For example:
            
            metadata = client.get_latest_binary("firefox")
        """
        
        pass
        

    @callback
    def get_available_binary_versions(self, package):
        """
            get_available_binary_versions(package)
            
            - package is the name of the package. 
            
            This function will return a list of available package versions.
            
            For example:
            
            versions = client.get_available_binary_versions("firefox")
        """
        
        pass

    
    @callback
    def get_binary_version(self, package, version):
        """
            get_binary_version(package, version)
            
            - package is the name of the package. 
            - version is the version of the package.
            
            This function will return the metadata of a package with matching
            version or None if it does not exist.
            
            For example:
            
            metadata = client.get_available_binary_versions("firefox")
        """
        
        pass

       
    @callback
    def mark_package(self, package):
        """
            mark_package(package)
            
            - package is the name of the package.
            
            This function will mark a package and any necessary dependencies to
            be downloaded when apply_changes is called.
            
            For example:
            
            package = client.get_latest_binary("firefox")
            client.mark_package(package)
        """
        
        pass
        
    
    @callback
    def apply_changes(self, reporthook=None, callback=None):
        """
            apply_changes(reporthook=None)
            
            - reporthook is a function name that will be called to report the 
              progress of files as they are being downloaded. If omitted, the
              function will print out progress into the console.
            
            This function will download marked packages and change their status
            from "to be downloaded" to "to be installed".
            
            For example:
            
            client.apply_changes()
        """
        
        pass
        
        
    @callback
    def save_changes(self, filename):
        """
            save_changes(status)
            
            - filename is the filename where the status information will be
              written.
              
            This function will write the status information to file. This is
            used primarily for saving packages that are marked as
            "to be downloaded" or "to be installed" so they may be retrieved at
            a later time.
            
            When implementing this function, it should write data in EXACTLY
            the same format as it was read in from the operating system.
            
            For example:
            
            client.save_changes("keryx_status")
        """
        
        pass
        
        
    @callback
    def install(self, reporthook=None, callback=None, root="gksu", status="/var/lib/dpkg/status"):
        """
            install(root="gksu", reporthook=None)
            
            - directory is the location of the downloaded packages and lists.
              It must have the following folder structure:
                directory
                directory/lists
                directory/packages
                
              This guarantees the unwrapt will be able to find both the lists
              and packages in the subdirectories of 'directory'.
            
            - root is the application called to request the user for root
              access. This is typically "gksu" for graphical users or "sudo"
              for CLI users.
            
            - reporthook is the name of a function that will report the
              progress of installation.
              
            This function will install the packages that are marked as
            "to be installed"
            
            For example:
            
            client.install()
        """
        
        pass    
        
        
    @callback
    def get_changes_size(self):
        """
            get_changes_download_size()
            
            This function will return the number of packages that will be 
            cahnged and an approximate amount of bytes that will be downloaded 
            when apply_changes is called.
            
            For example:
            
            (number_of_packages, size_text, size_in_bytes) = client.get_changes_download_size()
            
            print number_of_packages
            3
            
            print size_text 
            '3.6 MB'
            
            print size_in_bytes
            3774873
        """
        
        pass
        
        
    @callback
    def get_package_status(self, package):
        """
            get_package_status()
            
            - package is the name of the package
            
            This funciton will return the status of the package requested.
            
            For example:
            
            client.get_package_status("firefox")
        """
        
        pass
        
        
    @callback
    def get_package_version(self, package):
        """
            get_package_version()
            
            - package is the name of the package
            
            This funciton will return the installed version of the package 
            requested.
            
            For example:
            
            client.get_package_version("firefox")
        """
        
        pass
        
        
    @callback
    def cancel_changes(self, downloads, installs):
        """
            cancel_changes(downloads, installs)
            
            - downloads set to True will cancel any pending package downloads
            that were marked.
            
            -installs set to True will cancel any pending package installations
            that were marked.
            
            This function will remove all pending "to be downloaded" 
            
            For example:
            
            client.cancel_changes(downloads=True, installs=True)
        """
        
        pass
        
        
    @callback
    def get_upgrades(self):
        """
            get_upgrades()
            
            Returns a list of package metadata that are newer versions than the
            ones currently installed. These items can be marked and installed
            as upgrades.
            
            For example:
            
            upgrades = client.get_upgrades()
        """
        
        pass
        
    @callback
    def has_to_be_installed(self):
        """
            has_to_be_installed()
            
            Returns a boolean whether or not the client has packages marked as
            to be installed.
            
            For example:
            
            # Check if we need to install any packages
            if client.has_to_be_installed():
                client.install()
        """
