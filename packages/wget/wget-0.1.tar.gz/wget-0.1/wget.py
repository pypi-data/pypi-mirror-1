"""
The sole purpose of this module to provide easy to remember way of downloading
files with out-of-the-box Python installation:

    python -m wget <URL>


This module should probably be renamed to something else before incorporated
into Python library to avoid complains about missing options, but it is hard
to invent something more intuitive (like 'fetch').
"""

import sys, urllib, shutil, os


if len(sys.argv) < 2:
    sys.exit("No download URL specified")


(filename, headers) = urllib.urlretrieve(sys.argv[1])
# copy filename, because it will be destroyed on exit
shutil.copy(filename, ".")
os.unlink(filename)


print headers
print "Saved under %s" % os.path.basename(filename)

"""
features that require more tuits for urlretrieve API
http://www.python.org/doc/2.6.4/library/urllib.html#urllib.urlretrieve

[ ] autodetect filename for saving file (from URL, from headers)
[ ] catch KeyboardInterrupt
[ ] optionally preserve incomplete file and notify about its location
[ ] start downloading directly into current directory to save incomplete file
[ ] resume download (broken download)
[ ] resume download (incomplete file)
[ ] show progress indicator
    http://mail.python.org/pipermail/tutor/2005-May/038797.html
"""
