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

# from win32gui_taskbar was I untimely ripped :)
from win32api import *
from win32gui import *
import win32con
import sys, os

dd = os.path.dirname(os.path.abspath(__file__))
# If not with source-code, use sys.prefix, which is where distutils puts them.
if not os.path.isdir(os.path.join(dd, "base")):
    dd = os.path.join(sys.prefix, 'spats')

class MainWindow:
    def __init__(self, svc):
        msg_TaskbarRestart = RegisterWindowMessage("TaskbarCreated");
        message_map = {
                msg_TaskbarRestart: self.OnRestart,
                win32con.WM_DESTROY: self.OnDestroy,
                win32con.WM_COMMAND: self.OnCommand,
                win32con.WM_USER+20 : self.OnTaskbarNotify,
        }
        # Register the Window class.
        wc = WNDCLASS()
        hinst = wc.hInstance = GetModuleHandle(None)

        # get the service name
        wc.lpszClassName = svc

        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        wc.hCursor = LoadCursor( 0, win32con.IDC_ARROW )
        wc.hbrBackground = win32con.COLOR_WINDOW
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        classAtom = RegisterClass(wc)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = CreateWindow( classAtom, "Enfold Controller", style, \
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, \
                0, 0, hinst, None)
        UpdateWindow(self.hwnd)
        self._DoCreateIcons()

    def _DoCreateIcons(self):
        # Try and find a custom icon
        hinst =  GetModuleHandle(None)

        iconPathName = os.path.join(dd, r"base\favicon.ico")
        print "*", iconPathName
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        hicon = LoadImage(hinst, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)

        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, "Enfold Controller")
        Shell_NotifyIcon(NIM_ADD, nid)

    def OnRestart(self, hwnd, msg, wparam, lparam):
        self._DoCreateIcons()

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0) # Terminate the app.

    def OnClose(self, hwnd, msg, wparam, lparam):
        DestroyWindow(self.hwnd)

    def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
        if lparam==win32con.WM_RBUTTONUP:
            menu = CreatePopupMenu()
            AppendMenu( menu, win32con.MF_STRING, 1025, "Stop Enfold Controller" )
            pos = GetCursorPos()
            # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
            SetForegroundWindow(self.hwnd)
            TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)
            PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
        return 1

    def OnCommand(self, hwnd, msg, wparam, lparam):
        id = LOWORD(wparam)
        if id == 1025:
            DestroyWindow(self.hwnd)

def start():
    w=MainWindow("Enfold Controller")
    PumpMessages()

def stop():
    sys.exit()

def __call__(server, spats):
    # not much to do here
    start()

if __name__=='__main__':
    start()
