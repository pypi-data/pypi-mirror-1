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

import webbrowser
import time
import sys

try:
    import splash
except ImportError:
    pass
    # allow non win32 clients

def __call__(server_address, spats):
    # start the browser pointing to our instance
    server, port = server_address
    if not server:
        server = "localhost"
    url = "http://%s:%s/" % (server, port)
    webbrowser.open(url)
    print "Press Ctrl+C to shut down the XController"
    try:
        splash.Close()
    except NameError:
        pass
    while 1:
        try:
            time.sleep(0.5)
            if not spats.running:
                break

        except KeyboardInterrupt:
            sys.exit(1)
