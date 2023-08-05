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

import locale, gettext, sys, os

root = __file__
if os.path.islink(root):
    root = os.path.realpath(root)
moduleroot = os.path.dirname(os.path.abspath(root)) 

## Try to setup the proper locale to get i18n started:
localedir = os.path.join(moduleroot, "locale")

try:
    loc = locale.setlocale( locale.LC_ALL, "" ) # This sets the locale to the system's default.
except:
    print "And now for something completely different..."
    print "setlocale failed. Please report this to us."
    raise SystemExit
            
## REMEMBER:
## locale.getlocale() -- DON'T USE getlocale
## ALWAYS use locale.getpreferredencoding()
## On my system when LANG=C or LANG=
## This returns "ANSI_X3.4-1968"

## The .mo file is called "all.mo"
domain = "all"
gettext.install( domain, localedir, unicode = True )

try:
    lang = gettext.translation (domain, localedir, languages=[loc])#have to have last param ...
    lang.install(unicode = True )

except IOError:
    ## Could not find the domain.mo file.
    pass # default to English.

