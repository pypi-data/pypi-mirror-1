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


# MFC (win32ui) dialog that hosts an IE control
# Must be a dialog for keyboard accels to work correctly in the IE control.

from pywin.mfc import dialog, window, activex
from pywin.framework import dlgappcore
import win32ui, win32uiole
import win32con
import win32gui
import win32help
import os, sys, win32api, glob
from win32com.client import gencache
import util
import splash
from urllib import unquote

WM_KICKIDLE = 0x036A

url_start = None
spats = None
title = 'encontrol'

_htmlhelp_handle = None
_htmlhelp_hwnd = None
def htmlhelp_do(hwnd, path, cmd, arg=None):
    global _htmlhelp_hwnd, _htmlhelp_handle
    if _htmlhelp_handle is None:
        _htmlhelp_hwnd, _htmlhelp_handle = win32help.HtmlHelp(hwnd, None, win32help.HH_INITIALIZE)
    win32help.HtmlHelp(hwnd, path.encode('mbcs'), cmd, arg)

def htmlhelp_cleanup():
    if _htmlhelp_handle is not None:
        win32help.HtmlHelp(0, None, win32help.HH_UNINITIALIZE, _htmlhelp_handle)

def MakeDlgTemplate():
    style = (win32con.WS_MINIMIZEBOX
             | win32con.WS_THICKFRAME
             | win32con.DS_MODALFRAME
             | win32con.WS_POPUP
             | win32con.WS_VISIBLE
             | win32con.WS_CAPTION
             | win32con.WS_SYSMENU
             | win32con.DS_SETFONT)
    # this should be setable elsewhere
    dlg = [[title, (0, 0, 450, 350),
            style, None, (8, "MS Sans Serif")],]
    return dlg

WebBrowserModule = gencache.EnsureModule("{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}", 0, 1, 1)
if WebBrowserModule is None:
    raise ImportError, "IE does not appear to be installed."

class WebBrowser(activex.Control, WebBrowserModule.WebBrowser):
    # Was attempting to get reliable shutdown - the 'idle' check below works
    # fine, but I'll leave this here as reference:
    #def OnBeforeNavigate2(self, pDisp, URL, Flags, TargetFrameName, PostData, Headers, Cancel):
    #    print "BeforeNavigate2", pDisp, URL, Flags, TargetFrameName, PostData, Headers, Cancel
    #    print "OnBN", URL, spats.running
    #    # ack - can't make this cancel :(
    #    return True, None, True

    def OnNewWindow3(self, ppDisp, Cancel, dwFlags, bstrUrlContext, bstrUrl):
        #print "NewWindow", `bstrUrlContext`, `bstrUrl`
        if bstrUrl.startswith('spatshelp:'):
            ref = unquote(bstrUrl[10:].replace("$", "#"))
            ref = os.path.join(spats._config['help_dir'], ref)
            htmlhelp_do(self.GetSafeHwnd(), ref, win32help.HH_DISPLAY_TOPIC)
            # cancel the event
            return 0, None, True

    #def OnNavigateError(self, pDisp, URL, Frame, StatusCode, Cancel):
    #    """Fired when a binding error occurs (window or frameset element)."""

class IEDialog(dlgappcore.AppDialog):
    def OnInitDialog(self):
        self.HookMessage(self.OnKickIdle, WM_KICKIDLE)
        self.HookMessage(self.OnSize, win32con.WM_SIZE)
        rc = dlgappcore.AppDialog.OnInitDialog(self)
        self.olectl = WebBrowser()
        try:
            client_rect = self.GetClientRect()
            control_flags = (win32con.WS_TABSTOP
                             | win32con.WS_VISIBLE)
            self.olectl.CreateControl("OCX", control_flags,
                                      client_rect, self._obj_, 131)
        except win32ui.error:
            self.MessageBox("The IE Control could not be created")
            self.olectl = None
            self.EndDialog(win32con.IDCANCEL)
            return 0
        try:
            self.olectl.SetFocus()
            self.SetForegroundWindow()
        except win32ui.error:
            pass
        # Setup an icon if spats is so configured.
        if spats is not None and 'icon_filename' in spats._config:
            icon_filename = spats._config['icon_filename']
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(0, icon_filename, win32con.IMAGE_ICON, 0, 0, icon_flags)
            win32gui.SendMessage(self.GetSafeHwnd(), win32con.WM_SETICON, win32con.ICON_BIG, hicon)

        self.olectl.Navigate(url_start)
        splash.Close()
        return rc

    def PreDoModal(self):
        pass

    def OnOK(self):
        # So an 'enter' key doesn't bring us down.
        return 0

    # This also prevents the close button working :(  Ideally we need a URL
    # to redirect direct to in this case.
    #def OnCancel(self):
    #    # So an 'escape' key doesn't bring us down.
    #    return 0

    def OnSize(self, params):
        left, top, right, bottom = self.GetClientRect()
        self.olectl.MoveWindow((left, top, right-left, bottom-top))

    def OnKickIdle(self, msg):
        if spats is not None and not spats.running:
            self.EndDialog(0)

class Application(dlgappcore.DialogApp):
    def CreateDialog(self):
        return IEDialog(MakeDlgTemplate())
    def ExitInstance(self):
        htmlhelp_cleanup()
        dlgappcore.DialogApp.ExitInstance(self)

def run(url):
    global url_start
    url_start = url
    # And bootstrap the app.
    app=Application()
    try:
        app.InitInstance()
    except win32ui.error:
        raise ImportError, "Sorry - you need a new win32ui.pyd for this to work"
    app.Run()

def __call__(server, _spats):
    global spats
    spats = _spats
    # needs an absolute path
    abs = util.getDirectory()
    addr, port = server
    if not addr:
        addr = "localhost"
    url = "http://%s:%s/" % (addr, port)
    run(url)

if __name__=='__main__':
    print "Testing open of", sys.argv[1]
    run(sys.argv[1])
