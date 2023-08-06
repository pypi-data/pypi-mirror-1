Quick Overview
==============

Spats or Simple PAge Template Server is an attempt to make a
simple little Page Template Server that can be used by
everyone. Basically the idea is simple, allow you to serve out a
Page Template back to a http request. It subclass all the Python
standard library HTTP servers to do this.

You can also have Python Scripts which are for the more advanced logic
of serving out bits and peices.

Dependencies
============

SimpleTAL, although we might need to make a more complicated one soon
to deal with i18n. SimpleTAL can be found here::
 
  http://www.owlfish.com/software/simpleTAL/

Optional Dependencies
=====================

wxembed: Using a wxPython to embed the server and IE win to make it
look like an application. Requires wx.
    
mfcembed: Using a win32ui native wrapper to embed the server and IE
win to make it look like an application. A better choice for Windows
users. Requires pywin32.
    
taskbar: Makes a little windows taskbar icon. Again only for Windows
and requires pywin32.
    
browser: Just runs in the command line and fires up a browser. No
dependencies for this one ;)
