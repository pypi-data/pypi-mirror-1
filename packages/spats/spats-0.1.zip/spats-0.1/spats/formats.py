# spats  |  Copyright(C), 2004-2007, Enfold Systems, LLC
#
#
# Enfold Systems, LLC
# 4617 Montrose Blvd., Suite C215
# Houston, Texas 77006 USA
# p. +1 713.942.2377 | f. +1 832.201.8856
# www.enfoldsystems.com
# info@enfoldsystems.com
#
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of the
# License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

formats = {}

# this should always work
import browser
formats["browser"] = browser

try:
    pass
    # only if wxpython is around
    #import wxembed
    #formats["wxembed"] = wxembed
except ImportError:
    pass

try:
    # only if win32api is around
    import taskbar
    formats["taskbar"] = taskbar
except ImportError:
    pass

try:
    # Things can get upset with a mismatch of pywintypesXX.dll etc in
    # system32 versus the version in our site-packages.  Explicitly
    # importing them ensures the site-packages one is loaded.
    import pywintypes, pythoncom
    # Only if pywin32's mfc support is around
    import mfcembed
    formats["mfcembed"] = mfcembed
except ImportError, why:
    pass

# should always work
import server
formats["server"] = server

def getFormats():
    return formats

def getFormat(format):
    return formats[format]



# we prefer MFC-embed as we get tab keys
# Next up is wxembed - no tab keys, but still looks like an "app"
# Last preference is hosting in a browser.
def getOrder():
    return ["mfcembed", "wxembed", "browser", "taskbar", "server"]
