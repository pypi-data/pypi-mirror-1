#!/usr/bin/python
# encoding: utf-8

#    babtools_gentoo - Simple tools for Gentoo users and ebuild dabblers. 
# 
#    Copyright © 2008 Arne Babenhauserheide
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

"""babtools_gentoo: Some tools for working with Gentoo.
 

Usage: 
 - babtools_gentoo.py cmd [OPTIONS]
   
   for default usage, or 
   
 - babtools_gentoo.py --help
   
   for getting help
 

Avaible commands: 
 - ebuild_to_local CP
   
   CP (cathegory/package) in the simple form dev-lang/python or similar. CPVs (cathegory/package-version) aren't supported, yet. 
    
 - ebuild_download_to_local CP URL
  
   Download an ebuild from bugs.gentoo.org to the local portage tree.    
   
 - emerge_from_pypi PACKAGE
  
   Create an ebuild from a project in PyPI, put it into package.keywords and install it. 
   Honors package.keywords directories. 
   It only puts the directly named PACKAGE into package.keywords as dev-python/PACKAGE
   but doesn't put the dependencies into package.keywords. 
 

Examples: 
 - sudo babtools_gentoo.py ebuild_to_local dev-lang/python
   
   copy dev-lang/python into the local overlay
   
 - sudo babtools_gentoo.py ebuild_download_to_local games-rpg/vegastrike http://bugs.gentoo.org/attachment.cgi?id=151789
   
   Download the ebuild for games-rpg/vegastrike from bugs.gentoo.org and digest it. 
  
 - sudo babtools_gentoo.py emerge_from_pypi magma
   
   Create an ebuild for "magma" from the PyPI and emerge it. 


Source URL (Mercurial): U{http://freehg.org/u/ArneBab/babtools_gentoo/}

PyPI URL: U{http://pypi.python.org/pypi/babtools_gentoo}
"""

# We need to be able to join paths and to check, if something's a dir or a file. 
from os.path import join, isdir, isfile, join

# And to creade directories, and list the contents of a directory. 
from os import makedirs, listdir

# And to copy files. 
from shutil import copytree, copy

# Now we need the portage settings to get the overlays. 
from portage import settings as portage_settings

PORTAGE_DIR = portage_settings["PORTDIR"]
# We just try the options for the local overlay. If it exists, we use it. 
#: A list of possible locations of the overlay. At the moment: deprecated version and new (standardized for multiple overlays) version. 
possible_local_overlays = ["/usr/local/portage", "/usr/portage/local/local-overlay"]
for i in possible_local_overlays: 
    if isdir(i) and i in portage_settings["PORTDIR_OVERLAY"]: 
        local_overlay = i
# If that worked, we can now assign it. 
try: 
    PORTAGE_LOCAL = local_overlay
except: 
    raise Exception("local overlay not found in " + str(possible_local_overlays))

verbose = True

PACKAGE_KEYWORDS = join(join("/etc", "portage"), "package.keywords")

def copy_ebuild_to_local_overlay(CP):  
    """Copy the ebuild dir to the local overlay.
    
    TODO implement cleanly, no hardcoded paths and such."""
    
    #: The system dir containing the ebuild
    EBUILD_DIR = join(PORTAGE_DIR, CP)
    #: The local dir containing the ebuild
    EBUILD_DIR_LOCAL = join(PORTAGE_LOCAL, CP)
    
    # If the dir of the ebuild exists
    if isdir(EBUILD_DIR): 
        # Check if a local dir already exists. 
        if isdir(EBUILD_DIR_LOCAL):
            # If yes, copy all files inside the dir to the local dir. 
            for i in listdir(EBUILD_DIR): 
                FILEPATH_TMP = join(EBUILD_DIR, i)
                if isfile(FILEPATH_TMP): 
                    copy(FILEPATH_TMP, EBUILD_DIR_LOCAL)
            if verbose: 
                print "copied all contents of", EBUILD_DIR, "over to", EBUILD_DIR_LOCAL
        
        else: 
            # If the cathegory exists, only copy over the dir of the ebuild, 
            if isdir(join(PORTAGE_LOCAL, CP.split("/")[0])): 
                copytree(EBUILD_DIR, join(PORTAGE_LOCAL, CP.split("/")[0]))
            
                if verbose: 
                    print "copied dir", EBUILD_DIR, "over to", EBUILD_DIR_LOCAL
            
            # else create the cathegory first.     
            else: 
                # Create the cathegory dir. 
                makedirs(join(PORTAGE_LOCAL,join(PORTAGE_LOCAL, CP.split("/")[0])))
                if verbose: 
                    print "created the cathegory dir", join(PORTAGE_LOCAL,join(PORTAGE_LOCAL, CP.split("/")[0]))
                # And copy over the ebuild. 
                copytree(EBUILD_DIR, EBUILD_DIR_LOCAL)
                if verbose: 
                    print "and copied the dir", EBUILD_DIR, "to", EBUILD_DIR_LOCAL
        
    # If the given package atom doesn't lead to a directory, just cry out loud :) 
    else: 
        raise Exception("package atom doesn't point to an existing ebuild dir.")
    

def download_ebuild_to_local_overlay(CP, URL):
    """Download an ebuild from a given URL to the given CP in the local tree."""
    
    #: The local dir containing the ebuild
    EBUILD_DIR_LOCAL = join(PORTAGE_LOCAL, CP)
    
    from urllib2 import urlopen
    
    # First get the file and its name. 
    urlfile = urlopen(URL)
    # Get the header containing the name
    name_header = name = urlfile.headers.values()[-1]
    # We get something in the form 'text/plain; name="vegastrike-0.5.0.ebuild"; charset=UTF-8'
    # Check that we really get that. 
    assert name_header[:10] == "text/plain"
    
    #Now extract the name from it. 
    filename = name_header.split(";")[1].strip()[6:-1]
    
    # Now make sure the local ebuild dir exists. 
    create_local_ebuild_dir(CP)
    
    # And save the file there. 
    diskfile = open(join(EBUILD_DIR_LOCAL, filename), "w")
    diskfile.write(urlfile.read())
    diskfile.close()
    
    # Since we now created a plain ebuild file without manifest, we still need to digest it. 
    # We do this wit a bashcall (yes, that's lazy, but it works, and well). 
    # First we change into the ebuilds dir. 
    from os import chdir
    chdir(EBUILD_DIR_LOCAL)
    
    # Now we call the ebuild utility. 
    from subprocess import call
    call("ebuild " + filename + " digest", shell=True)
    
    # Done. 
    

def create_local_ebuild_dir(CP):
    """Create the ebuild dir in the local portage tree, if it doesn't exist."""
    
    EBUILD_DIR_LOCAL = join(PORTAGE_LOCAL, CP)
    
    # If the local dir doesn't exists, create it. 
    if not isdir(EBUILD_DIR_LOCAL): 
        makedirs(EBUILD_DIR_LOCAL)


def add_to_package_keywords(CP):
    """Add a cathegory/package to package.keywords. Honor package.keywords directories. """
    # First we assemble the CP string to write to the keywords. 
    string_to_write = "\n# Package added by babtools_gentoo"
    string_to_write += "\n" + CP
        
    # First we check, if package.keywords is a directory. 
    if isdir(PACKAGE_KEYWORDS): 
        # If package.keywords is a directory, we check, if CP is inside the file python inside it. 
        python_keywords_file = open(join(PACKAGE_KEYWORDS, "python"), "r")
        if not CP in python_keywords_file.read(): 
            # If CP isn't in the file, 
            # Remember to close the file first. 
            python_keywords_file.close()
            # Then append the CP to the file. 
            python_keywords_file = open(join(PACKAGE_KEYWORDS, "python"), "a")
            python_keywords_file.write(string_to_write)
            # And remember to close the file again. 
        else: 
            print CP + " is already inside the package.keywords"
        python_keywords_file.close()
    else: 
        # If package.keywords is a file, we just append the CP to package.keywords, if it isn't already inside it. 
        keywords_file = open(PACKAGE_KEYWORDS, "r")
        if not CP in keywords_file.read(): 
            # First close the file properly. 
            keywords_file.close()
            # Then add the CP. 
            keywords_file = open(PACKAGE_KEYWORDS, "a")
            keywords_file.write(string_to_write)
        else: 
            print CP + " is already inside the package.keywords"
        # And remember to close it. 
        keywords_file.close()
        

def emerge_from_pypi(PACKAGE):
    """Create an ebuild directly from PyPI.
    
        - Create the ebuild with g-pypi
        - put it into package.keywords (if it's a dir, put it into the file python inside the dir)
        - emerge it via portage. 
        """
    # First we need to be able to call shell commands. 
    from subprocess import call
    
    # We now create CP from the PACKAGE
    CP = "dev-python/" + PACKAGE
    
    # Now we call g-pypi to create the ebuild. 
    if verbose: 
        print "Creating ebuild for " + CP + " via g-pypi."
    call("g-pypi " + PACKAGE, shell=True)
    
    if verbose: 
        print "\nPutting " + CP + " into the package.keywords, if it isn't already there."
    # Then we put dev-python/PACKAGE into package.keywords
    add_to_package_keywords(CP)
    
    if verbose: 
        print "\nFinally emerging " + CP + "."
    # And emerge it via a shellcall to portage/emerge. 
    call("emerge " + CP, shell=True)
    
    # At the end, say what we did. 
    print "\nFinished installing " + CP + "."


def print_help(): 
    """Display help and a list of commands."""
    # Just print the second paragraph of the docstring (paragraphs seperated by really empty lines). 
    print __doc__.split("\n\n")[1]
    # Print two empty lines. 
    print ""
    print ""
    list_commands()
    # Print two empty lines. 
    print ""
    print ""
    print_examples()

def list_commands():
    """List avaible commands."""
    # Just print the third paragraph of the docstring. 
    print __doc__.split("\n\n")[2]
    
def print_examples():
    """List avaible commands."""
    # Just print the fourth paragraph of the docstring. 
    print __doc__.split("\n\n")[3]

#### Self-Test ####

def _test(): 
    from doctest import testmod
    testmod()

if __name__  == "__main__": 
    
    from sys import argv
    # If we get no args, print the help. 
    if len(argv) == 1: 
       print "We need a command as argument, for example 'ebuild_to_local'." 
       print_help()
    # If we get the help argument, print help, too. 
    elif argv[1] == "help" or argv[1] == "--help" or argv[1] == "-h": 
        print_help()
        
    # If we get no argument for ebuild_to_local, print an error. 
    elif argv[1] == "ebuild_to_local" and len(argv) == 2: 
        print "'ebuild_to_local' needs a valid package atom as argument (like dev-lang/python)."
    
    # If we get a valid looking request for ebuild_to_local, 
    # copy the ebuild directory  given by the package atom to the 
    # local portage tree. 
    elif argv[1] == "ebuild_to_local" and len(argv) == 3: 
        copy_ebuild_to_local_overlay(argv[2])
    
    # if we get a download request with valid package atom, 
    # download it to the local portage tree. . 
    elif argv[1] == "ebuild_download_to_local": 
        if len(argv) < 4: 
            print_help()
        else: 
            download_ebuild_to_local_overlay(CP=argv[2], URL=argv[3])
    
    # If we get the request to directly install a package from the PyPI, then get it. 
    
    elif argv[1] == "emerge_from_pypi": 
        if len(argv) < 3: 
            print_help()
        else: 
            emerge_from_pypi(PACKAGE=argv[2])
    else: 
        print "command not recognized:", argv[1]
        print_help()
    
    #_test()
