import gzip
import os
from Download import *

def url_join(*args):
    return "/".join([x.strip("/") for x in args])

def packages_url(repo, arch, fmt):
    return url_join(repo["url"], arch, "Packages%s" % fmt)

def filename_from_url(url, directory=''):
    return os.path.join(directory, url.split("//")[1].replace("/", "_"))

def format_number(number, SI=0, space=' '):
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
    else: format = '%.0f%s%s'

    return(format % (float(number or 0), space, symbols[depth]))









class Unwrapt:
    def __init__(self, arch, repos):
        self.architecture = self.__parse_arch(arch)
        self.repositories = self.__parse_repos(repos)
        self.download_dir = os.getcwd()
        self.packages = {}


    def update(self):
        downloads = []

        # Download latest package lists
        for repo in self.repositories:
            display = "Repository => %s / %s" % (repo["dist"], repo["section"])
            url = packages_url(repo, self.architecture, ".gz")
            #downloads.append(self.download(url, "lists", display))
            #except Exception, e: print "There was a problem while downloading %s: %s" % (url, e)

        self.__parse_packages(downloads)
        print "%i packages available" % len(self.packages)


    def __parse_packages(self, filenames):
        self.packages = {}

        for repo in self.repositories:
            f = gzip.open(os.path.join(self.download_dir,"lists",filename_from_url(packages_url(repo, self.architecture, ".gz"))), 'rb')
            self.__parse_packages_file(repo, f)
            f.close()


    def __parse_packages_file(self, repo, f):
        package = {}

        for line in f:
            # Package is finished parsing
            if line.startswith("\n"):
                package["Repository"] = repo
                self.__add_package(package)
                package = {}

            # Long description
            elif line.startswith(" ") or line.startswith("\t"):
                if "Long" in package: package["Long"] += line
                else:                 package["Long"] = line

            else:
                key, value = line.split(": ", 1)
                package[key] = value.strip()


    def __add_package(self, package):
        """Adds a package to the internal package dictionary"""
        pkg_name = package["Package"]

        names = [package["Package"]]
        if "Provides" in package:
            names += [p.strip() for p in package["Provides"].split(",")]

        for name in names:
            if name in self.packages: self.packages[name].append(package)
            else:                     self.packages[name] = [package]


    def download(self, url, destination, display=None, reporthook=textprogress):
        """Download files to destination"""
        if not display: display = url

        output_dir = os.path.join(self.download_dir, destination)
        output_file = os.path.join(output_dir, filename_from_url(url))

        # Create output directory if it doesn't exist already
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        download_url(url, output_file, display)
        return output_file


    def __parse_arch(self, arch):
        """Clean and format architecture"""
        supported = ["amd64", "armel", "i386", "ia64", "powerpc", "sparc"]
        if arch in supported: return "binary-%s" % arch
        else: raise AttributeError, "%s is not a supported architecture" % arch


    def __parse_repos(self, repositories):
        """Parse repos for sections"""
        parsed = []

        for repo in self.__filter_repos(repositories):
            try: rtype, url, dist, sections = repo.split(None, 3)
            except: raise AttributeError, "Invalid format for %s" % repo

            for section in sections.split():
                parsed.append({
                    "rtype": rtype,
                    "main_url": url,
                    "dist": dist,
                    "section": section,
                    "url": url_join(url, "dists", dist, section)
                    })

        return parsed


    def __filter_repos(self, repositories):
        """Clean and filter repositories list"""
        # Remove whitespace and inline comments
        repos = [r.strip().split("#")[0] for r in repositories]
        return filter(lambda r: r.startswith("deb "), repos)








if __name__ == "__main__":
    repos = """#deb cdrom:[Ubuntu 10.10 _Maverick Meerkat_ - Release amd64 (20101007)]/ maverick main restricted
# See http://help.ubuntu.com/community/UpgradeNotes for how to upgrade to
# newer versions of the distribution.

deb http://us.archive.ubuntu.com/ubuntu/ maverick main restricted
deb-src http://us.archive.ubuntu.com/ubuntu/ maverick main restricted

## Major bug fix updates produced after the final release of the
## distribution.
deb http://us.archive.ubuntu.com/ubuntu/ maverick-updates main restricted
deb-src http://us.archive.ubuntu.com/ubuntu/ maverick-updates main restricted

## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu
## team. Also, please note that software in universe WILL NOT receive any
## review or updates from the Ubuntu security team.
deb http://us.archive.ubuntu.com/ubuntu/ maverick universe
deb-src http://us.archive.ubuntu.com/ubuntu/ maverick universe
deb http://us.archive.ubuntu.com/ubuntu/ maverick-updates universe
deb-src http://us.archive.ubuntu.com/ubuntu/ maverick-updates universe

## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu 
## team, and may not be under a free licence. Please satisfy yourself as to 
## your rights to use the software. Also, please note that software in 
## multiverse WILL NOT receive any review or updates from the Ubuntu
## security team.
deb http://us.archive.ubuntu.com/ubuntu/ maverick multiverse
deb-src http://us.archive.ubuntu.com/ubuntu/ maverick multiverse
deb http://us.archive.ubuntu.com/ubuntu/ maverick-updates multiverse
deb-src http://us.archive.ubuntu.com/ubuntu/ maverick-updates multiverse

## Uncomment the following two lines to add software from the 'backports'
## repository.
## N.B. software from this repository may not have been tested as
## extensively as that contained in the main release, although it includes
## newer versions of some applications which may provide useful features.
## Also, please note that software in backports WILL NOT receive any review
## or updates from the Ubuntu security team.
# deb http://us.archive.ubuntu.com/ubuntu/ maverick-backports main restricted universe multiverse
# deb-src http://us.archive.ubuntu.com/ubuntu/ maverick-backports main restricted universe multiverse

## Uncomment the following two lines to add software from Canonical's
## 'partner' repository.
## This software is not part of Ubuntu, but is offered by Canonical and the
## respective vendors as a service to Ubuntu users.
# deb http://archive.canonical.com/ubuntu maverick partner
# deb-src http://archive.canonical.com/ubuntu maverick partner

## This software is not part of Ubuntu, but is offered by third-party
## developers who want to ship their latest software.
deb http://extras.ubuntu.com/ubuntu maverick main
deb-src http://extras.ubuntu.com/ubuntu maverick main

deb http://security.ubuntu.com/ubuntu maverick-security main restricted
deb-src http://security.ubuntu.com/ubuntu maverick-security main restricted
deb http://security.ubuntu.com/ubuntu maverick-security universe
deb-src http://security.ubuntu.com/ubuntu maverick-security universe
deb http://security.ubuntu.com/ubuntu maverick-security multiverse
deb-src http://security.ubuntu.com/ubuntu maverick-security multiverse"""

    u = Unwrapt("amd64", repos.split("\n"))
    u.update()
