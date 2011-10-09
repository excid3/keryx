# -*- coding: utf-8 -*-
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

"""
    Our packages are stored in the following format in self.packages

    {"package name": [{version1}, {version2}, {version3}],
     "package two": [{version1}]}

     This allows us to easily find a package, as well as all the versions
"""


import gzip
import httplib
import logging
import os
import shutil
import subprocess
import sys
import urllib
import urlparse

from datetime import datetime

#from Download import download_url, textprogress, httpExists
#from utils import format_number, to_filename, to_url, url_join

#from DpkgVersion import DpkgVersion

SUPPORTED = ["Ubuntu"]

#TODO: Add resume support: http://code.activestate.com/recipes/83208-resuming-download-of-a-file/

class InvalidCredentials(Exception):
    """Exception raised if the proxy credentials are invalid"""
    pass

class ProxyOpener(urllib.FancyURLopener):
    """Class for handling proxy credentials"""
    def __init__(self, proxy={}, usr=None, pwd=None):
        urllib.FancyURLopener.__init__(self, proxy)
        self.count = 0
        self.proxy = proxy
        self.usr = usr
        self.pwd = pwd

    def prompt_user_passwd(self, host, realm):
        """Override the FancyURLopener prompt and simply return what was given
           Raise an error if there is a problem
        """
        self.count += 1

        if self.count > 1:
            raise InvalidCredentials, "Unable to authenticate to proxy"

        return (self.usr, self.pwd)

def textprogress(url, display, current, total):
    """Download progress in terminal"""
    percentage = current/float(total) * 100

    sys.stdout.write("\r%-56.56s %3i%% [%5sB / %5sB]" % \
        (display,
         percentage,
         format_number(current),
         format_number(total)))

    if percentage == 100:
        sys.stdout.write("\n")

    # This makes sure the cursor ends up on the far right
    # Without this the cursor constantly jumps around
    sys.stdout.flush()


def download_url(url, filename, display=None, progress=textprogress, proxy={}, username=None, password=None):
    """Downloads a file to ram and returns a string of the contents"""
    if not display:
        display = url.rsplit("/", 1)[1]

    # Do we already have a file to continue off of?
    # modified determines whether the file is outdated or not based on headers
    modified = None
    downloaded = 0
    if os.path.exists(filename):
        modified = datetime.utcfromtimestamp(os.stat(filename).st_mtime)
        downloaded = os.path.getsize(filename)

    # Open up a temporary connection to see if the file we have downloaded
    # is still usable (based on modification date)
    # format meanings are located http://docs.python.org/library/time.html
    opener = ProxyOpener(proxy, username, password)
    headers = opener.open(url).headers

    if modified and "Last-Modified" in headers:
        dt = datetime.strptime(headers["Last-Modified"],
                                        "%a, %d %b %Y %H:%M:%S %Z")

        # File is too old so we delete the old file
        if modified < dt:
            #logging.debug("OLD FILE")
            #print "OLD FILE"
            downloaded = 0
            os.remove(filename)

    # Test existing filesize compared to length of download
    if "Content-Length" in headers:
        length = int(headers["Content-Length"])

        # File already downloaded?
        if downloaded == length:
            progress(url, "Hit: %s" % display, length, length)
            return

        # File corrupted?
        elif downloaded > length:
            downloaded = 0
            os.remove(filename)

    # Open up the real connection for downloading
    opener = ProxyOpener(proxy, username, password)
    if downloaded:
        opener.addheader("Range", "bytes=%s-" % str(downloaded))
    page = opener.open(url)

    # The file range must have matched the download size
    if not "Content-Length" in page.headers:
        progress(url, "Hit: %s" % display, downloaded, downloaded)
        return

    # Finish downloading the file
    length = int(page.headers["Content-Length"]) + downloaded
    f = open(filename, "ab")

    while 1:
        data = page.read(8192)
        if not data:
            break
        downloaded += len(data)
        f.write(data)
        progress(url, display, downloaded, length)
    f.close()
    page.close()

    return

##Check for Valid URL based on the HTTP response code
def httpExists(url):
    host, path = urlparse.urlsplit(url)[1:3]
    found = False
    connection = httplib.HTTPConnection(host)  ## Make HTTPConnection Object
    try:
        connection.request("HEAD", path)
        responseOb = connection.getresponse()      ## Grab HTTPResponse Object
        if responseOb.status == 200:
            found = True
    except:
        pass

    return found

def url_join(*args):
    """ Returns full URL """
    # Strip any leading or trailing slashes from the parts.
    args = [x.strip("/") for x in args]

    return "/".join(args)


def to_url(repository, architecture, format):
    return url_join(repository["url"], architecture, format)


def to_filename(directory, url):
    """
       Forms a full filename from a directory and url.
       i.e. Strips the url of the protocol prefix, replaces all slashes with 
       underscores, and appends it to directory.
    """
    return os.path.join(directory, url.split("//")[1].replace("/", "_"))


def format_number(number, SI=0, space=' '):
    """
        Turn numbers into human-readable metric-like numbers
        Used from the urlgrabber library
    """
    symbols = ['',  # (none)
               'k', # kilo
               'M', # mega
               'G', # giga
               'T', # tera
               'P', # peta
               'E', # exa
               'Z', # zetta
               'Y'] # yotta
    
    if SI: step = 1000.0
    else: step = 1024.0

    thresh = 999
    depth = 0
    max_depth = len(symbols) - 1
    
    # we want numbers between 0 and thresh, but don't exceed the length
    # of our list.  In that event, the formatting will be screwed up,
    # but it'll still show the right number.
    while number > thresh and depth < max_depth:
        depth  = depth + 1
        number = number / step

    if type(number) == type(1) or type(number) == type(1L):
        # it's an int or a long, which means it didn't get divided,
        # which means it's already short enough
        format = '%i%s%s'
    elif number < 9.95:
        # must use 9.95 for proper sizing.  For example, 9.99 will be
        # rounded to 10.0 with the .1f format string (which is too long)
        format = '%.1f%s%s'
    else:
        format = '%.0f%s%s'
        
    return(format % (float(number or 0), space, symbols[depth]))

###############################################################################
# Custom Exceptions
###############################################################################

class PermissionsError(Exception):
    """Unable to run command under current user permissions"""
    pass

class UnsupportedArchitecture(Exception):
    """Project attempted to use an unsupported architecture type"""
    pass

class PackageAlreadySet(Exception):
    """Package is being marked when it already has a status set"""
    pass

class InvalidRepository(Exception):
    """A repository string was passed that is invalid or not supported"""
    pass

###############################################################################
# The AptDef
###############################################################################

#TODO: Append package to dict in its own place, but also under each item it provides

class Apt:

    proxy = {"proxy": {},
             "user": None,
             "pass": None}

    packages = {}
    status = {}
    supported = ["amd64", "armel", "i386", "ia64", "powerpc", "sparc"]
    status_properties = ["Package", "Version", "Status", "Provides"]
    binary_dependencies = ["Pre-Depends", "Depends", "Recommends"]
    supported_statuses = ["install ok installed",
                          "to be downloaded",
                          "dependency to be downloaded",
                          "to be installed",
                          "dependency to be installed"]

    def set_architecture(self, architecture):
        """set architecture"""

        if architecture == "x86_64":
            architecture = "amd64"

        if not architecture in self.supported:
            raise UnsupportedArchitecture

        self.architecture = "binary-%s" % architecture


    def set_repositories(self, repositories):
        """set repositories list"""
        self.repositories = []
        for repo in repositories:
            repo = repo.split('#')[0].strip()  # Remove inline comment, if one exists.
            if repo:
                #try:
                    rtype, url, dist, sections = repo.split(None, 3)

                    for section in sections.split():
                        r = {}
                        r["rtype"] = rtype
                        r["url"] = url
                        r["dist"] = dist
                        r["section"] = section
                        r["url"] = url_join(url, "dists", dist, section)

                        self.repositories.append(r)
                #except Exception:
                #    raise InvalidRepository, \
                #        "Repository is either invalid or not supported: %s" % repr(repo)



    def __iter_repositories(self):
        """
            Used for iterating through the repository entries
            This function yields Repository objects and creates them as needed
        """
        for repo in self.repositories:
            if repo["rtype"] == "deb":
                yield repo


    def update(self, reporthook=None, callback=None, download=True):
        """
            This is a missing docstring ZOMG!
            callback should be a tuple of the function, and any arguments to be passed

            callback=(glib.idle_add, self.function_to_call)
        """

        if download:
	    #try:
		#logging.info("Downloading latest package lists...")
            self._download_lists(reporthook)
	    #except Exception, e:
		#logging.error(e)

        self._read_lists()

        if callback:
            callback[0](*callback[1:])

    def _download_lists(self, reporthook=None):
        """on_update helper function"""

        if not reporthook:
            reporthook = textprogress

        directory = os.path.join(self.download_directory, "lists")

        # If the download directory does not exist, create it
        if not os.path.exists(directory):
            os.makedirs(directory)

        for repo in self.__iter_repositories():

            # Build the strings
            url = to_url(repo, self.architecture, "Packages")
            filename = to_filename(directory, url)
            display_name = "Repository => %s / %s" % (repo["dist"], repo["section"])

            # Download
            #TODO: catch exceptions
            #TODO: Support bz2 and unarchived Packages files
            filename = "%s.gz" % filename
            url_with_ext  = "%s.gz" % url

            #Checks the sources.list URL are valid and downloads the repo files
            if httpExists(url_with_ext):
            	download_url(url_with_ext,
                                filename,
                                display_name,
                                progress=reporthook,
                                proxy=self.proxy["proxy"],
                                username=self.proxy["user"],
                                password=self.proxy["pass"])
            else:
                logging.error("\nURL not exist: %s" % url_with_ext)


    def _build_lists(self, directory, lists=[]):

        # Build the strings
        for repo in self.__iter_repositories():
            url = to_url(repo, self.architecture, "Packages")
            filename = to_filename(directory, url)
            filename = "%s.gz" % filename  # Works only if the index files are gz
            lists.append((repo, filename))

        return lists


    def _read_lists(self, reporthook=None):
        """on_update helper function"""

        def defaulthook(string):
            """ Default report hook fallback """
            if string:
                sys.stdout.write("\r%s" %string)
            else:
                sys.stdout.write("\n")
            sys.stdout.flush()


        if not reporthook:
            reporthook = defaulthook

        self.packages = {}
        lists = self._build_lists(os.path.join(self.download_directory, "lists"))
        total = len(lists)

        # Now parse each file, extracting as necessary
        for i, value in enumerate(lists):
            repo, filename = value

            # Display percent read
            frac = (float(i)/float(total))*100
            reporthook("Reading package lists... %3i%%" % frac)

 	    # Attempt to open the package list.
            try:
                if filename.endswith(".gz"):
                    f = gzip.open(filename, "rb")
                else:
                    f = open(filename, "rb")
                # Parse packages into dictionary
                self.__parse(repo, f)
                f.close()
            except IOError , ioex:
                # Process the value of Errno and display the respective error message
                if ioex.errno:
                    # If Errno value is 2, then the file is not exists
                    if ioex.errno == 2:
                        logging.error("\nPackage list does not exist: %s" % filename)
                else:
                    logging.error("\n%s: %s" % (ioex,filename))
                    # If we receive a corrupted package list delete it
                    os.remove(filename)

                #TODO: Redownload the corrupted list and hope that parses :)

        reporthook("Reading package lists... %3i%%" % 100)
        reporthook("")
        logging.info("%i packages available" % len(self.packages))


    def __parse(self, repo, f):
        """
            Takes a repository and an open file

            returns a dictionary with all packages in file
        """

        current = {}
        for line in f:

            # Do we have a filled out package?
            if line.startswith("\n"):

                # Attach
                current["Repository"] = repo
                if current["Package"] in self.packages:
                    self.packages[current["Package"]].append(current)
                else:
                    self.packages[current["Package"]] = [current]

                current = {}

            # Do we have a long description?
            elif line.startswith(" ") or line.startswith("\t"):
                if "Long" in current:
                    current["Long"] += line
                else:
                    current["Long"] = line

            # Everything else is a standard property that gets handled the same
            else:
                try:
                    key, value = line.split(": ", 1)
                    current[key] = value.strip()
                except Exception, e:
                    logging.debug(repr(line))
                    logging.debug(e)


    def on_set_status(self, status="/var/lib/dpkg/status"):
        """
            Parses the dpkg status file for package versions, names, and
            installed statuses.
        """

        f = open(status, "rb")

        self.status = {}

        current = {}
        for line in f:

            # Add package metadata to status
            if line.startswith("\n") and "Package" in current:

                # Only add package if it is a supported status
                if current["Status"] in self.supported_statuses:
                    self.status[current["Package"]] = current

                    # Mark the provides as well for dependency calculation
                    if "Provides" in current:
                        for provide in current["Provides"].split(", "):
                            self.status[provide] = current

                current = {}

            else:
                # Add property
                try:
                    key, value = line.split(": ", 1)

                    if key in self.status_properties:
                        current[key] = value.strip()
                except:
                    pass

        f.close()

        logging.info("%i packages installed" % len(self.status))


    def on_get_available_package_names(self):
        return self.packages.keys()


    def on_get_latest_binary(self, package):
        """
            Returns the data for latest version of a package
        """

        available = self.get_available_binary_versions(package)

        if not available:
            return None

        # Set the DpkgVersion instance for each package
        for pkg in available:
            pkg["DpkgVersion"] = DpkgVersion(pkg["Version"])

        # Compare the versions
        newest = available[0]
        for pkg in available[1:]:
            if pkg["DpkgVersion"] > newest["DpkgVersion"]:
                newest = pkg

        return newest


    def on_get_binary_version(self, package, version):

        available = self.get_available_binary_versions(package)

        # Return the metadata of the package with matching version
	for package in available:
            if DpkgVersion(package["Version"]) == version:
                return package

        return None


    def on_get_available_binary_versions(self, package):
        """
            Return a list of metadata for all available packages with a
            matching name
        """

        if not package in self.packages:
            return []

        return self.packages[package]


    def on_mark_package(self, metadata, dependency=False):
        """
            Get a list of dependencies based on package metadata
        """

        if not metadata:
            raise AttributeError, "You must supply valid package metadata"

        #TODO: This function obviously needs to be split up and modularized :)

        # First check if the package is installed already?
        if self.__is_installed(metadata["Package"]) and \
           not self.__is_upgradable(metadata["Package"]):
            raise AttributeError, "Package %s is already %s." % (metadata["Package"], self.get_package_status(metadata["Package"]))

        # Mark the package itself
        if not dependency: metadata["Status"] = "to be downloaded"
        else: metadata["Status"] = "dependency to be downloaded"
        self.status[metadata["Package"]] = metadata

        logging.info("Finding dependencies for %s..." % metadata["Package"])

        depends = self.on_get_package_dependencies(metadata)

        # Do the dependency calculations
        for dep in depends:

            # In case we have some ORs
            options = dep.split(" | ")

            satisfied = False
            for option in options:

                details = option.split(" ")
                name = details[0]

                # If any of these packages are already installed
                if name in self.status:
                    #logging.debug("Dependency %s installed!" % name)

                    # Assume installed version will work
                    satisfied = True

                    # Test for compatible version just in case
                    if len(details) > 1:
                        comparison = details[1][1:] # strip the '('
                        version = details[2][:-1] # strip the ')'

                        satisfied = DpkgVersion(self.status[name]["Version"]). \
                                            compare_string(comparison, version)

                    # No need to test the other options if one is found
                    if satisfied:
                        break

            # No package was installed, so take the first one and add it
            # as a dependency
            if not satisfied:

                name = options[0].split(" ", 1)[0]
                pkg = self.get_latest_binary(name)

                #TODO: Verify pkg's version satisfies
                #pkg["Status"] = "to be downloaded"
                #self.status[pkg["Package"]] = pkg
                #print pkg

                # Mark sub-dependencies as well
                if pkg:
                    self.on_mark_package(pkg, dependency=True)


    def on_get_package_dependencies(self, metadata):

        # Build a string of the necessary sections we need
        depends = []
        for section in self.binary_dependencies:
            if section in metadata:
                depends += metadata[section].split(", ")

        return depends


    def on_apply_changes(self, reporthook=None, callback=None):

        if not reporthook:
            reporthook = textprogress

        directory = os.path.join(self.download_directory, "packages")

        # Build the list of package urls to download
	packages = [(key, self.get_binary_version(value["Package"], value["Version"])) \
	            for key, value in self.status.items() \
		    if value["Status"] in ["to be downloaded", "dependency to be downloaded"]]

        downloads = [(key, value["Repository"]["url"].split("dists")[0] + value["Filename"]) \
                     for key, value in packages]

        #downloads = []
        #for key, value in self.status.items():
        #    if value["Status"] == "to be downloaded":
        #        downloads.append(value["Repository"]["url"].split("dists")[0] + value["Filename"])

        logging.info("%i packages to be installed" % len(downloads))

        # Create the download directory if it doesn't exist
        if not os.path.exists(directory):
            os.mkdir(directory)

        # Download the files
        for key, url in downloads:
            download_url(url,
                         "%s/%s" % (directory, url.rsplit("/", 1)[1]),
                         progress=reporthook,
                         proxy=self.proxy["proxy"],
                         username=self.proxy["user"],
                         password=self.proxy["pass"])
            # Once it's downloaded, mark this package status to "to be installed"
            # or "dependency to be installed", depending on what it is now.
            if self.status[key]["Status"] == "to be downloaded":
                self.status[key]["Status"] = "to be installed"
            elif self.status[key]["Status"] == "dependency to be downloaded":
                self.status[key]["Status"] = "dependency to be installed"

        if callback:
            callback[0](*callback[1:])


    def on_save_changes(self, status):

        # This will NOT create a status file to override /var/lib/dpkg/status
        # so DO NOT try to replace the system status file.
        # YOU HAVE BEEN WARNED

        f = open(status, "wb")

        for status, package in self.status.items():

            # Try to write these back in the order they were read
            properties = ["Package", "Status", "Version", "Provides"]
            lines = ["%s: %s\n" % (key, package[key]) for key in properties if key in package]

            f.writelines(lines)
            f.write("\n")

        f.close()


    def on_cancel_changes(self, downloads, installs):

        for key, value in self.status.items():
            if downloads and value["Status"] in \
                    ["to be downloaded", "dependency to be downloaded"] or \
               installs and value["Status"] in \
                    ["to be installed", "dependency to be installed"]:
                del self.status[key]


    def on_get_changes_size(self):
        #TODO: If we pass the downloads directory, we can get a more accurate
        # list of files to download (if the file sizes match)

        # Build list of packages to be downloaded
        packages = [(value["Package"], value["Version"]) \
                    for key, value in self.status.items() \
                    if value["Status"] in ["to be downloaded", "dependency to be downloaded"]]

        count = 0
        total = 0
        for name, version in packages:
            package = self.get_binary_version(name, version)
            if package:
                total += int(package["Size"])
                count += 1

        return (count, format_number(total), total)


    def on_get_package_status(self, package):

        if package in self.status:
            return self.status[package]["Status"]

        return "not installed"


    def on_get_package_version(self, package):

        if package in self.status:
            return self.status[package]["Version"]

        return None


    def on_install(self, reporthook=None, callback=None, root="gksu", status="/var/lib/dpkg/status"):
        """
            We will take the approach of installing by copying the lists to
            /var/lib/apt/lists and the packages to /var/cache/apt/archives and
            calling apt-get update and then apt-get install on the packages
            which have the status of "to be installed". This prevents tampering
            with sources.list and works more or less the exact same if we made
            a local repository.
        """

	def subproc(command):
	    if reporthook:
		reporthook(command)

	    logging.info(command)
	    return subprocess.call(command, shell=True)

        # Copy lists over
        for repo in self.__iter_repositories():
            url = to_url(repo, self.architecture, "Packages")
            source = to_filename(os.path.join(self.download_directory, "lists"), url)
	    dest = to_filename("/var/lib/apt/lists", url)

	    subproc("%s \"sh -c 'zcat %s.gz > %s'\"" % (root, source, dest))


        # Copy packages over
	files = []
        for value in self.status.values():
            if value["Status"] in ["to be installed", "dependency to be installed"]:
                pkg_filename = self.get_binary_version(value["Package"], value["Version"])["Filename"].rsplit("/", 1)[1]
                files.append(os.path.join(self.download_directory, "packages", pkg_filename))

	subproc("%s \"sh -c 'cp %s /var/cache/apt/archives/'\"" % (root, " ".join(files)))


        # Call apt-get install with the packages
        packages = [value["Package"] for key, value in self.status.items() if value["Status"] == "to be installed"]


	subproc("%s apt-cache gencaches" % root)
        subproc("%s \"sh -c 'apt-get install -y %s'\"" % (root, " ".join(packages)))

        # Update the status after installation
        self.set_status(status)

	if callback:
	    callback[0](*callback[1:])


    def on_get_upgrades(self):

        upgrades = []

        # We will only check the installed packages, anything to be downloaded
        # or installed can wait. We might want to change this in the future.
        installed = [value for key, value in self.status.items() if value["Status"] == "install ok installed"]

        for current in installed:
            latest = self.get_latest_binary(current["Package"])

            # Only if there is a version available should we check to see if
            # there is a newer version. We also don't want to mark it twice if
            # the package is already selected for upgrade
            if latest and latest not in upgrades and DpkgVersion(latest["Version"]) > DpkgVersion(current["Version"]):
                upgrades.append(latest)

        return upgrades


    def has_to_be_installed(self):
        for package in self.status.values():
            if package["Status"] == "to be installed":
                return True
        return False


    def __is_installed(self, package):
        """Take a package name, returns True if installed, False otherwise."""

        status = self.on_get_package_status(package)
        if status != "install ok installed":
            return False
        return True


    def __is_upgradable(self, package):
        """Takes a package name, returns True if installed and out-of-date,
           False otherwise.
        """

        if not self.__is_installed(package):
            return False  #FIXME: should we raise an error?
        current = self.status[package]
        latest = self.get_latest_binary(package)
        if latest and DpkgVersion(latest["Version"]) > DpkgVersion(current["Version"]):
            return True
        else:
            return False
