#!/usr/bin/env python
##    fui Copyright (C) 2008 Donn.C.Ingle
##    Contact: donn.ingle@gmail.com - I hope this email lasts.
##
##    This file is part of fui.
##    fui is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    fui is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with fui.  If not, see <http://www.gnu.org/licenses/>.


import os, sys, glob, fnmatch
from distutils.core import setup, Extension
import distutils.command.install_data

import fuimodules.i18n # to install gettext for fuimodules.strings
import fuimodules.strings

## Code borrowed from wxPython's setup and config files
## Thanks to Robin Dunn for the suggestion.
## I am not 100% sure what's going on, but it works!
def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)

# Specializations of some distutils command classes
class wx_smart_install_data(distutils.command.install_data.install_data):
    """need to change self.install_dir to the actual library dir"""
    def run(self):
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return distutils.command.install_data.install_data.run(self)

def find_data_files(srcdir, *wildcards, **kw):
    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data
    def walk_helper(arg, dirname, files):
        if '.svn' in dirname:
            return
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)
                if ".pyc" not in filename:
                    if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                        names.append(filename)
        if names:
            lst.append( (dirname, names ) )

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list

## This is a list of files to install, and where:
## Make sure the MANIFEST.in file points to all the right 
## directories too.
files = find_data_files('fuimodules/', '*.*')

setup(name = fuimodules.strings.appname,
    version = fuimodules.strings.version,
    description = fuimodules.strings.description,
    author = "Donn.C.Ingle",
    author_email = fuimodules.strings.contact,
    license = fuimodules.strings.licence,
    url = fuimodules.strings.url,
    packages = ['fuimodules'],
    data_files = files,
    ## Borrowed from wxPython too:
    ## Causes the data_files to be installed into the modules directory.
    ## Override some of the default distutils command classes with my own.
    cmdclass = { 'install_data': wx_smart_install_data },

    scripts = [fuimodules.strings.appname],
    long_description = fuimodules.strings.long_description,
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'Intended Audience :: End Users/Desktop',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Operating System :: POSIX :: Linux',
      'Programming Language :: Python',
      'Topic :: Utilities',
      ]
)
