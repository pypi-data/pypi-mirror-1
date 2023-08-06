#!/usr/bin/env python
# encoding: utf-8

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

"""Some tools for working with Gentoo.

Avaible commands: 
 - ebuild_to_local CP
 
   CP (cathegory/package) in the simple form dev-lang/python or similar. CPVs (cathegory/package-version) aren't supported, yet. 
   
 - ebuild_download_to_local CP download_url
 
   Download an ebuild from bugs.gentoo.org to the local portage tree.    

Source URL (Mercurial): U{http://freehg.org/u/ArneBab/babtools_gentoo/}

PyPI URL: U{http://pypi.python.org/pypi/babtools_gentoo}
"""

# We need to be able to join paths and to check, if something's a dir or a file. 
from os.path import join, isdir, isfile

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
    

def download_ebuild_to_local_overlay(CP, download_url):
    """Download an ebuild from a given URL to the given CP in the local tree."""
    
    #: The local dir containing the ebuild
    EBUILD_DIR_LOCAL = join(PORTAGE_LOCAL, CP)
    
    from urllib2 import urlopen
    
    # First get the file and its name. 
    urlfile = urlopen(download_url)
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
    

def print_help(): 
    """Display help and a list of commands."""
    print "Usage: babtools_gentoo.py cmd [OPTIONS]"
    print "  or: babtools_gentoo.py --help"
    print ""
    list_commands()

def list_commands():
    """List avaible commands."""
    
    print "Avaible commands: "
    print " - ebuild_to_local CP"
    print "   CP (cathegory/package) in the simple form dev-lang/python or similar. CPVs (cathegory/package-version) aren't supported, yet. "
    print ""
    print " - ebuild_download_to_local CP download_url"
    print "   Download an ebuild from bugs.gentoo.org to the local portage tree. "

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
            download_ebuild_to_local_overlay(CP=argv[2], download_url=argv[3])
    else: 
        print "command not recognized:", argv[1]
        print_help()
    
    #_test()
