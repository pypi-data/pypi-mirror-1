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

# a wx wrapper around the thing

import wx
import win32api
import win32gui
import win32con
import util
import time
import splash

server_address = None

if wx.Platform == '__WXMSW__':
    import wx.lib.iewin as iewin

class exHtmlPanel(wx.Panel):
    def __init__(self, parent, id, frame):
        wx.Panel.__init__(self,parent,-1)

        self.ie = iewin.IEHtmlWindow(self, -1, style = wx.NO_FULL_REPAINT_ON_RESIZE)

        # needs an absolute path
        abs = util.getDirectory()
        addr, port = server_address
        if not addr:
            addr = "localhost"
        url = "http://%s:%s/" % (addr, port)

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.ie, 1, wx.GROW)

        self.ie.LoadUrl(url)

        self.SetSizer(self.box)
        self.SetAutoLayout(True)

class exFrame (wx.Frame):
    def __init__(self, parent, ID, title):
        size = wx.Size(600, 500)
        wx.Frame.__init__(self,parent,ID,title,wx.DefaultPosition,size)
        panel = exHtmlPanel(self, -1, self)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, evt):
        assert wx.GetApp().spats, "Don't have a spats?"
        wx.GetApp().spats.stop()

class exApp(wx.App):
    spats = None

    def OnInit(self):
        # this should be set elsewhere
        frame = exFrame(None, -1, "encontrol")
        frame.Show(True)
        self.SetTopWindow(frame)
        splash.Close()
        return True

    def MainLoop(self):
        # Create an event loop and make it active.  If you are
        # only going to temporarily have a nested event loop then
        # you should get a reference to the old one and set it as
        # the active event loop when you are done with this one...
        evtloop = wx.EventLoop()
        old = wx.EventLoop.GetActive()
        wx.EventLoop.SetActive(evtloop)

        # This outer loop determines when to exit the application,
        # for this example we let the main frame reset this flag
        # when it closes.
        while self.spats.running:
            # At this point in the outer loop you could do
            # whatever you implemented your own MainLoop for.  It
            # should be quick and non-blocking, otherwise your GUI
            # will freeze.

            # This inner loop will process any GUI events
            # until there are no more waiting.
            while evtloop.Pending():
                evtloop.Dispatch()

            # Send idle events to idle handlers.  You may want to
            # throttle this back a bit somehow so there is not too
            # much CPU time spent in the idle handlers.  For this
            # example, I'll just snooze a little...
            time.sleep(0.10)
            self.ProcessIdle()

        wx.EventLoop.SetActive(old)

def __call__(server, spats):
    global server_address
    server_address = server

    app = exApp(0)
    app.spats = spats
    app.MainLoop()

if __name__=='__main__':
    print "Please use start.py to start this application"
