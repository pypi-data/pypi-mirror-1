# A splash screen for spats apps.  Comes with a default splash-screen, but
# each app can spefify its own.  Its up to each app to call the Show() method
# itself to get the splash-screen, and up to each 'format' to close the Window
# (The 'format' must close it as the splash window can not be destroyed until
# the main window is created for 'foreground window' semantics to work).
# A thread is started to kill the splash after 5 seconds, just in case a
# non-splash-aware 'format' is used (currently only mfcembed is aware)

import pywintypes # ensure a local copy is preferred over system32.
from win32gui import *
import win32con
import threading
import os
import time

# A message we post, so any thread can kill the splash-screen.
WM_CLOSESPLASH = win32con.WM_USER+30

class SplashScreen:
    def __init__(self, image_filename, set_topmost = True, title = 'encontrol'):
        self.image_filename = image_filename
        self.set_topmost = set_topmost
        self.hwnd = 0
        self.title = title # only ever seen in the taskbar

    def Show(self):
        # Create a new thread for the window, so it can run its own message
        # loop without upsetting the main thread, so the window can be
        # repainted as the main app starts.
        t = threading.Thread(target = self.Run)
        t.setDaemon(False)
        t.start()

    def Close(self):
        PostMessage(self.hwnd, WM_CLOSESPLASH, 0, 0)

    def Run(self):
        self.Initialize()
        PumpMessages()

    def Initialize(self):
        message_map = {
                win32con.WM_DESTROY: self.OnDestroy,
                win32con.WM_PAINT: self.OnPaint,
                WM_CLOSESPLASH: self.OnCloseSplash,
        }

        # Register the Window class.
        wc = WNDCLASS()
        hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = "EnfoldSplash"
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        wc.hbrBackground = GetStockObject(win32con.NULL_BRUSH)
        classAtom = RegisterClass(wc)

        # Load the bitmap and fill out a BITMAP structure for it

        hbm = LoadImage(0, self.image_filename,
                        win32con.IMAGE_BITMAP, 0, 0, win32con.LR_LOADFROMFILE)
        bm = GetObject(hbm)
        DeleteObject(hbm)

        # Get the extents of the desktop window
        left, top, right, bottom = GetWindowRect(GetDesktopWindow())

        # Create a centered window the size of our bitmap
        hWnd = CreateWindow(classAtom, self.title,
                            win32con.WS_POPUP | win32con.WS_BORDER, # style
                            (right  / 2) - (bm.bmWidth  / 2),
                            (bottom / 2) - (bm.bmHeight / 2),
                            bm.bmWidth,
                            bm.bmHeight,
                            0, 0, 0, None)
        # Make Window topmost if requested
        if self.set_topmost:
            SetWindowPos(hWnd, win32con.HWND_TOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        ShowWindow(hWnd, win32con.SW_SHOWNORMAL)
        UpdateWindow(hWnd)
        try:
            SetForegroundWindow(hWnd)
        except error: # win32gui.error
            pass # our parent no longer has focus.
        self.hwnd = hWnd

    def DrawBitmap(self, hWnd):
        # Get the extents of our window
        left, top, right, bottom = GetClientRect(hWnd)

        # Load the resource as a DIB section
        hBitmap = LoadImage(0, self.image_filename,
                            win32con.IMAGE_BITMAP, 0, 0,
                            win32con.LR_LOADFROMFILE | win32con.LR_CREATEDIBSECTION)

        bm = GetObject(hBitmap)

        # Get the DC for the window
        hdcWindow = GetDC(hWnd)

        # Create a DC to hold our surface and select our surface into it
        hdcMemory = CreateCompatibleDC(hdcWindow)
        SelectObject(hdcMemory, hBitmap)

        # Originally taken from an MS sample showing how to do high-color
        # splash-screens - we don't need to yet (nor does pywin32 do all we
        # need)
        #// Retrieve the color table (if there is one) and create a palette
        #// that reflects it
        #if (GetDIBColorTable(hdcMemory, 0, 256, rgbq))
        #    hPalette = CreatePaletteFromRGBQUAD(rgbq, 256);
        #else
        #    hPalette = CreateSpectrumPalette();
        #
        #// Select and realize the palette into our window DC
        #SelectPalette(hdcWindow,hPalette,FALSE);
        #RealizePalette(hdcWindow);

        # Display the bitmap
        SetStretchBltMode(hdcWindow, win32con.COLORONCOLOR)
        StretchBlt(hdcWindow, 0, 0, right, bottom,
                   hdcMemory, 0, 0, bm.bmWidth, bm.bmHeight, win32con.SRCCOPY)

        # Clean up our objects
        DeleteDC(hdcMemory);
        DeleteObject(hBitmap);
        ReleaseDC(hWnd, hdcWindow);
        #DeleteObject(hPalette);

    # Message handlers
    def OnPaint(self, hwnd, msg, wparam, lparam):
        hdc, ps = BeginPaint(hwnd)
        self.DrawBitmap(hwnd);
        EndPaint(hwnd, ps)

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        PostQuitMessage(0)

    def OnCloseSplash(self, hwnd, msg, wparam, lparam):
        DestroyWindow(hwnd)

def _WaitThenClose(period):
    for i in range(period):
        time.sleep(1)
        if splash is None:
            break
    else:
        Close()

# A convenient public interface
splash = None

def Show(filename = None, set_topmost = True, timeout = 30):
    global splash
    if not filename:
        filename = os.path.join(os.path.dirname(__file__), "base", "img","splash.bmp")
    try:
        SetStretchBltMode
    except NameError:
        # old pywin32 - just don't display it!
        return
    splash = SplashScreen(filename, set_topmost)
    splash.Show()
    # The 'formats' must have special knowledge of the splash-screen for
    # foreground window semantics to work (in short, the splash must not be
    # closed before the 'format' window is created).  In case we are using
    # a splash-naive format, start a thread to kill it.
    t = threading.Thread(target=_WaitThenClose, args=(timeout,))
    t.setDaemon(0)
    t.start()

def Close():
    global splash
    if splash is not None:
        splash.Close()
        splash = None

# A test.
if __name__=='__main__':
    import time
    #ss = SplashScreen("splash.bmp")
    #ss.Show()
    #time.sleep(3)
    #ss.Close()
    #print "sleeping"
    #time.sleep(2)
    Show()
    time.sleep(2)
    Close()
