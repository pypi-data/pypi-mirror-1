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

"""Some tools for working with Gentoo."""

PORTAGE_DIR = "/usr/portage"
PORTAGE_LOCAL = "/usr/local/portage"

verbose = True


# We need to be able to join paths and to check, if something's a dir or a file. 
from os.path import join, isdir, isfile

# And to creade directories, and list the contents of a directory. 
from os import makedirs, listdir

# And to copy files. 
from shutil import copytree, copy

def copy_ebuild_to_local_overlay(package_atom):  
    """Copy the ebuild dir to the local overlay.
    
    TODO implement cleanly, no hardcoded paths and such."""
    
    EBUILD_DIR = join(PORTAGE_DIR, package_atom)
    EBUILD_DIR_LOCAL = join(PORTAGE_LOCAL, package_atom)
    
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
            if isdir(join(PORTAGE_LOCAL, package_atom.split("/")[0])): 
                copytree(EBUILD_DIR, join(PORTAGE_LOCAL, package_atom.split("/")[0]))
            
                if verbose: 
                    print "copied dir", EBUILD_DIR, "over to", EBUILD_DIR_LOCAL
            
            # else create the cathegory first.     
            else: 
                # Create the cathegory dir. 
                makedirs(join(PORTAGE_LOCAL,join(PORTAGE_LOCAL, package_atom.split("/")[0])))
                if verbose: 
                    print "created the cathegory dir", join(PORTAGE_LOCAL,join(PORTAGE_LOCAL, package_atom.split("/")[0]))
                # And copy over the ebuild. 
                copytree(EBUILD_DIR, EBUILD_DIR_LOCAL)
                if verbose: 
                    print "and copied the dir", EBUILD_DIR, "to", EBUILD_DIR_LOCAL
        
    # If the given package atom doesn't lead to a directory, just cry out loud :) 
    else: 
        raise Exception("package atom doesn't point to an existing ebuild dir.")
    
    
def print_help(): 
    """Display help and a list of commands."""
    print "Usage: babtools_gentoo.py cmd [OPTIONS]"
    print "  or: babtools_gentoo.py --help"
    print ""
    list_commands()

def list_commands():
    """List avaible commands."""
    print "Avaible commands: "
    print " - ebuild_to_local package_atom"
    print "   package_atom in the simple form dev-lang/python or similar. Complex atoms (or atoms with versions) aren't supported, yet. "

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
    elif argv[1] == "help" or argv[1] == "--help" or argv[1] == "-h": 
        print_help()
    elif argv[1] == "ebuild_to_local" and len(argv) == 2: 
        print "'ebuild_to_local' needs a valid package atom as argument (like dev-lang/python)."
    elif argv[1] == "ebuild_to_local" and len(argv) == 3: 
        copy_ebuild_to_local_overlay(argv[2])
    else: 
        print "command not recognized:", argv[1]
        print_help()
    
    #_test()
