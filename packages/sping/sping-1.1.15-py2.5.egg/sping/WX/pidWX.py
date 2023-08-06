# pidWX.py
# based on piddleWX.py -- a wxPython backend for PIDDLE
# Copyright (c) 2000  Paul & Kevin Jacobs
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
"""WXCanvas

This class implements a Sping plug-in drawing Canvas object that draws using wxPython, the
wxWindows Python language bindings into a GUI window.
"""
# Status as of version 1.0:
#
# -  All test cases work correctly!  (except for the symbol font)
#
# -  The full interactive canvas API is supported, but not extensively
#    tested.  However, the default status bar object displays interactive
#    events nicely.
#
# -  The drawing code has been separated into a SpingWxDc class that
#    enables any wxPython application to use Sping.pid methods as a
#    DeviceContext.
#
# History:
#
#    0.1     First release.  Most PIDDLE functionality is there.
#    0.5     PIL support and code factoring added by Jeffrey Kunce.
#    1.0     All PIDDLE functionality supported.  Rotated test, multiline text,
#            and pil image support added.
#
# Known Bugs:
#
# -  Due to limitations in wxWindows, some fonts will not display when rotated;
#    As the default GUI font is not true-type, it cannot be rotated, and
#    PiddleWX will automatically re-assign the offending font to a type face
#    that can.
#
#
# Extensions:
#
# -  The canvas init function can take up to two additional arguments, both
#    of which are on by default.  The first is a boolean which enables the
#    interactive mode when true.  The second is a boolean that will add a
#    status bar to the canvas when true.
#
# -  The canvas can handle a left button released mouse event.  It's
#    handler is called onClickUp and is similar to the other event handlers.
#    handlers.  The standard onClick event registers left-click button down
#    events.
#
# -  The canvas can switch between interactive and non-interactive modes using
#    the SetInteractive function
#
# -  The canvas also supports an onLeaveWindow event, to trap when the mouse
#    leaves the canvas window, but due to a wxWindows bug it may not work.
#
# Limitations:
#
# -  There is no symbol font support at the moment.  It should be possible
#    under MS Windows.  Not sure about UNIX (wxGTK).
#
# -  The default status bar cursor co-ordinates display may not behave
#    properly due to several bugs.
#
# TODO:
#
# -  Make the status bar more user-configurable.
#
# -  Support printing & generation of Postscript output (just because it is
#    easy to do).

import wx
from pidWxDc import SpingWxDc

__version__ = "1.0"
__date__    = "February 6, 2000"
__author__  = "Paul & Kevin Jacobs"

class _WXCanvasDefaultStatusBar(wx.StatusBar):
    """
    This status bar displays clear and quit buttons, as well as the
    location of the mouse and whether the left button is down.
    """

    def __init__(self, canvas):

        wx.StatusBar.__init__(self, canvas.window, -1)


        #  As of python2.5 / wx 2.8.0.1, the OnSize event gets
        #  sent after the window closes. This caused the call
        #  to GetFieldRect() in Relayout() to segfault on win32. - michal
        self.closed = False
        self.Parent.Bind(wx.EVT_CLOSE, self.OnClose)


        self.sizeChanged = False
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        self.SetFieldsCount(3)

        self.quitButton= wx.Button(self, -1, "Quit")
        self.clearButton = wx.Button(self, -1, "Clear")
        self.click = wx.CheckBox(self, -1, "Click")  # checked when the left button is pressed
        self.text = wx.StaticText(self, -1, "")

        self.Reposition()  # set up sizes for layout

        self.quitButton.Bind(wx.EVT_BUTTON, canvas._OnQuit)
        self.clearButton.Bind(wx.EVT_BUTTON, canvas._OnClear)


    def SetStatusText(self, s):
        self.text.SetLabel(s)


    def OnOver(self, x, y):
        self.SetStatusText(`x` + "," + `y`)
        self.Refresh()


    def OnClick(self, x, y):
        self.SetStatusText(`x` + "," + `y`)
        self.click.SetValue(True)
        self.Refresh()


    def OnLeaveWindow(self):
        self.click.SetValue(False)
        self.SetStatusText("")
        self.Refresh()


    def OnClose(self, evt):
        self.closed = True
        evt.Skip()
        

    def OnClickUp(self, x, y):
        self.click.SetValue(False)


    def OnSize(self, evt):
        self.Reposition()
        # Set a flag so the idle time handler will also do the repositioning.
        # It is done this way to get around a buglet where GetFieldRect is not
        # accurate during the wx.EVT_SIZE resulting from a frame maximize.
        self.sizeChanged = True


    def OnIdle(self, evt):
        if self.sizeChanged:
            self.Reposition()


    def Reposition(self):

        if self.closed: return

        # layout field 0 with Buttons for quit and clear

        field = self.GetFieldRect(0)
        self.quitButton.SetPosition(wx.Point(field.x, field.y))
        self.quitButton.SetSize(wx.Size(field.width/2, field.height) )
 
        self.clearButton.SetPosition(wx.Point(field.x + field.width/2, field.y))
        self.clearButton.SetSize(wx.Size(field.width/2, field.height) )
 
        # layout sizing of field 1 w/ check box

        field = self.GetFieldRect(1)
        self.click.SetPosition(wx.Point(field.x, field.y))
        self.click.SetSize(wx.Size(field.width, field.height))

        field = self.GetFieldRect(2)
        self.text.SetPosition(wx.Point(field.x+2, field.y+2))
        #self.text.SetSize(wx.Size(field.width, field.height))
     
        self.sizeChanged = False


############################################################################

class WXCanvas(SpingWxDc):

    def __init__(self, size=(300,300), name="spingWX", status_bar = None,
                 interactive = True, show_status = True):
        """
        Works like all other Sping.pid canvases, except with extra interactive
        controls:

        interactive enables the interactive parts of the Sping.pid API
        show_status controls if the default status bar is shown
        """
        
        window = wx.Frame(None, -1, "WXCanvas", wx.DefaultPosition, wx.Size(size[0], size[1]))
        window.Show(True)
        window.Raise()

        self.window = window

        # Resize the window so the client area is equal to the canvas size
        CSize = window.GetClientSizeTuple()

        # Only leave space for a status bar if it is specified
        if show_status:
            # (should eventually be a call to getStatusBarHeight())
            status_area = 20
        else:
            status_area = 0

        window.SetSize(wx.Size(size[0] + (size[0] - CSize[0]),
                               size[1] + (size[1] - CSize[1]+ status_area)))

        # This bitmap is used to buffer drawing commands.  It is set to the same
        # depth as the screen - explicitly changing it can cause errors when it
        # is blitted to the screen

        bmp = wx.EmptyBitmap(size[0], size[1])
        MemDc = wx.MemoryDC()
        MemDc.SelectObject(bmp)

        MemDc.Clear()

        self.MemDc = MemDc
        SpingWxDc.__init__(self, MemDc, size, name)

        self.window = window
        self.size = size

        # Different status bars can be substituted in by overriding self.sb
        self.sb = status_bar if status_bar else _WXCanvasDefaultStatusBar(self)
        self.window.SetStatusBar(self.sb)
            
        self.sb.Show(show_status)


        # The default behavior for ignoring events is to pass it only to the
        # status bar.

        # onClick: x,y is Canvas coordinates of mouseclick def
        def ignoreClick(canvas,x,y):
            canvas.sb.OnClick(x,y)
        self.onClick = ignoreClick

        # onOver: x,y is Canvas location of mouse
        def ignoreOver(canvas,x,y):
            canvas.sb.OnOver(x,y)
        self.onOver = ignoreOver

        # onKey: key is printable character or one of the constants above;
        #    modifiers is a tuple containing any of (modshift, modControl)
        def ignoreKey(canvas,key,modifiers):
            pass
        self.onKey = ignoreKey

        # onClickUp: This is an extension:  It registers mouse left-button up
        # events
        def ignoreClickUp(canvas,x,y):
            canvas.sb.OnClickUp(x,y)
        self.onClickUp = ignoreClickUp

        self.interactive = interactive

        wx.EVT_PAINT(window, self._OnPaint)
        wx.EVT_LEFT_DOWN(window, self._OnClick)
        wx.EVT_LEFT_UP(window, self._OnClickUp)
        wx.EVT_MOTION(window, self._OnOver)
        wx.EVT_CHAR(window, self._OnKey)
        # Does not seem to be generated as of wxPython 2.1.13
        wx.EVT_LEAVE_WINDOW(window, self._OnLeaveWindow)

        # onLeaveWindow: This is an extension; it is called when the mouse
        # leaves the canvas window
        def leaveWindow(canvas):
            canvas.sb.OnLeaveWindow()
        self.onLeaveWindow = leaveWindow


    ############################################################
    #  Event Managers for wxPython.  To override event handling, alter the
    #  Sping event handlers, not these

    def _OnClick(self, event):
        if self.interactive == False:
            return None
        if event.GetY() <= self.size[1]:
            self.onClick(self, event.GetX(), event.GetY())


    def _OnClickUp(self, event):
        if self.interactive == False:
            return None
        self.onClickUp(self, event.GetX(), event.GetY())


    def _OnOver(self, event):
        if self.interactive == False:
            return None
        if event.GetY() <= self.size[1]:
            self.onOver(self, event.GetX(), event.GetY())


    def _OnLeaveWindow(self, event):
        if self.interactive == False:
            return None
        self.onLeaveWindow(self)


    def _OnKey(self, event):
        # The following logic is OK for ASCII characters.  Others will need work.
        code = event.KeyCode
        key = None
        if code >= 0 and code < 256:
            key = chr(event.KeyCode)

        modifier = []

        if event.ControlDown():
            modifier.append('modControl')

        if event.ShiftDown():
            modifier.append('modshift')

        self.onKey(self, key, tuple(modifier) )


    def _OnPaint(self, event):
        dc = wx.PaintDC(self.window)
        dc.Blit(0,0,self.size[0],self.size[1],self.MemDc,0,0,wx.COPY)
        del dc


    def _OnQuit(self, event):
        """Closes the canvas.  Call to return control your application"""
        self.window.Close()


    def _OnClear(self, event):
        """Clears the canvas by emptying the memory buffer, and redrawing"""
        self.MemDc.Clear()
        dc = wx.ClientDC(self.window)
        dc.Blit(0,0,self.size[0],self.size[1],self.MemDc,0,0,wx.COPY)


    #############################################################

    #------------ canvas capabilities -------------
    def isInteractive(self):
        """Returns 1 if onClick and onOver events are possible, 0 otherwise."""
        return self.interactive

    def canUpdate(self):
        """Returns 1 if the drawing can be meaningfully updated over time (e.g.,
        screen graphics), 0 otherwise (e.g., drawing to a file)."""
        return True

    #------------ general management -------------
    def clear(self):
        self.Clear()
        dc  = wx.ClientDC(self.window)
        dc.Blit(0,0,self.size[0], self.size[1], self.MemDc,0,0,wx.COPY)
        
    def flush(self):
        """Copies the contents of the memory buffer to the screen and enters the
        application main loop"""

        dc = wx.ClientDC(self.window)
        dc.Blit(0,0,self.size[0],self.size[1],self.MemDc,0,0,wx.COPY)
        del dc

    def setInfoLine(self, s):
        """For interactive Canvases, displays the given string in the 'info
        line' somewhere where the user can probably see it."""
        if self.sb != None:
            self.sb.SetStatusText(s)



if __name__=="__main__":
    app = wx.App(redirect=False)
    canvas = WXCanvas()
    #import trace;trace.Trace().run('app.MainLoop()')
    app.MainLoop()
    
