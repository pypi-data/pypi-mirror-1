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

appname = "fui"
version = "0.0.7"
licence = """License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law"""

copyright = "Copyright (C) 2008 Donn.C.Ingle"

contact = "donn.ingle@gmail.com"

warranty = """This program is distributed in the
hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE.  See the GNU General Public License for
more details."""

allvars = { "appname":appname,"vers":version,"copyright":copyright,"lic":licence,"warranty":warranty,"contact":contact }

verString = _("""%(appname)s %(vers)s
%(copyright)s
%(lic)s""") % allvars

url = "http://pypi.python.org/pypi/fui"

## Cheese Shop stuff
description = _("""%(appname)s - select and copy/move files & Directories on the command-line in a way very similar to how it's done in a gui with copy/cut and paste.
""") % allvars

## This is ReStructuredText
long_description = _(r"""By *selecting* filenames/directories into a selection set you can add and remove names quite simply. Once done, you'd go to another directory (even in another console or tab) and then you can copy (or move) the selection to there.

(So, you can select some files using normal wildcards; here for example, all the png files):
  ``%(appname)s bling blang bong *.png``
(Then move to another folder) 
  ``cd someotherplace``
(Add some more files)
  ``%(appname)s socks shorts shirts`` 
(Then you decide you don't want *shorts* or *wibble.png*)
  ``%(appname)s --exclude shorts wibble.png``
(Now you want to copy those somewhere)
  ``cd whereIwantStuff``

  ``%(appname)s --copy``

(done!)

Copying/moving is done recursively when directories are involved. More help is available via --help

The idea was to imitate the process in a typical file-manager gui. I know there are many ways to do this with grep and backticks and other tricks, but I wanted a simple way that I could remember :)

**Caution:** This is alpha software and I have not tested it nearly enough. Don't go using it on your vital data because it might eat it all up. Certainly give it a go until you get the feel and start to trust it.

I hope it helps someone out there.
""") % allvars


## CLI STUFF
help=_("""%(appname)s [Options] [Files]
Files:
This is a list of filenames or directory names.
You can use all the tricks like `ls *.png` as long
as you use spaces to separate items.

You can also pipe names into %(appname)s, for example:
ls *.jpg | %(appname)s

%(appname)s's default mode is 'select'. This means that
to select files, you simply name them and use no
options, like this:
 %(appname)s a b c pic.jpg *.png cheese

To remove an item, say one that snuck-in during
a glob like *.jpg, you do this:
 %(appname)s --exclude tomato.jpg fish.jpg eggs.jpg

Finally, go to your target directory and, for
example, copy those files to it:
 %(appname)s --copy

To keep your selection do this:
 %(appname)s --keep --copy
Then you can use it again elsewhere.

Options:
  -v --version  Show program's version number and exit.
  -h --help     Show this help message and exit.
  -l --list     Show what's in the selection set.
  -f --flush    Clear the selection set.
  -e name ..[name] --exclude name ..[name]
                Exclude name (and any listed names 
                separated by spaces) from the selection
                set.
  -c --copy     Will copy all the named files or
                directories into the current directory.
                The list will be cleared after this
                unless you add -k or --keep
  -m --move     Does the same as -c, but moves the
                named items to the current directory.
  -k --keep     Signals move/copy to retain your 
                selection set so you can use it again.

%(appname)s - the fake copy/paste user interface !
===
%(copyright)s

%(warranty)s

Report bugs to %(contact)s
""") % allvars

