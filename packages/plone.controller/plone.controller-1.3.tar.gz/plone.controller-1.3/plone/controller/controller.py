#!/usr/bin/env python

# main app for PloneController. Establishes
# app and its frame; runs main loop.

import sys
import os
import traceback

if sys.platform == 'win32':
    # Import pythoncom and pywintypes as soon as possible, to make
    # sure they are found. This must happen before *any* import from
    # pywin32 when you're in a 'relocatable' python build, like the
    # Plone Windows Installer.
    import pythoncom
    import pywintypes

import wx
import wx.lib.mixins.inspection
import Notebook, config
from config import debug

assertMode = wx.PYAPP_ASSERT_EXCEPTION



class RunApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):

    def __init__(self, name, module, useShell, cluster):
        self.name = name
        self.pcModule = module
        self.useShell = useShell
        self.cluster = cluster
        wx.App.__init__(self, redirect=os.environ.has_key('DEBUG'))

    def Message(self, msg, type=wx.OK|wx.ICON_INFORMATION, 
                title="Plone Controller Message"):
        if config.debug: print msg
        dlg = wx.MessageDialog(self.frame, str(msg), title, type)
        dlg.ShowModal()
        dlg.Destroy()

    def Error(self, msg):
        if msg is None:
            msg = "An unforseen error occured."

        traceback.print_exc(file=sys.stdout)
        self.Message(msg, type=wx.OK|wx.ICON_ERROR, title="Controller Error")

    def OnInit(self):
        wx.Log_SetActiveTarget(wx.LogStderr())

        self.SetAssertMode(assertMode)
        self.Init()  # InspectionMixin

        frame = wx.Frame(None, -1, "Plone Controller: " + self.name, pos=(150,150), 
                         size=(200,100),
                         style=wx.DEFAULT_FRAME_STYLE, 
                         name="run controller")
        self.frame = frame
        frame.CreateStatusBar()


        if not self.cluster.getClients():
            self.Message(
"""The Plone Controller needs to be run from the directory containing your buildout.cfg file.

You should have also already run bin/buildout.""",
                title='Error',
                )
            frame.Close(True)
            return False

        ns = {}
        ns['wx'] = wx
        ns['app'] = self
        ns['module'] = self.pcModule
        ns['frame'] = frame
        
        # frame.SetMenuBar(menuBar)
        frame.Show(True)
        frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        win = self.pcModule.runTest(frame, frame)

        # a window will be returned if the demo does not create
        # its own top-level window
        if win:
            # so set the frame to a good size for showing stuff
            frame.SetSize((640, 480))
            # frame.Fit()
            win.SetFocus()
            self.window = win
            ns['win'] = win
            frect = frame.GetRect()

        else:
            # It was probably a dialog or something that is already
            # gone, so we're done.
            frame.Destroy()
            return True

        self.SetTopWindow(frame)
        self.frame = frame
        #wx.Log_SetActiveTarget(wx.LogStderr())
        #wx.Log_SetTraceMask(wx.TraceMessages)

        if self.useShell:
            # Make a PyShell window, and position it below our test window
            from wx import py
            shell = py.shell.ShellFrame(None, locals=ns)
            frect.OffsetXY(0, frect.height)
            frect.height = 400
            shell.SetRect(frect)
            shell.Show()

            # Hook the close event of the test window so that we close
            # the shell at the same time
            def CloseShell(evt):
                if shell:
                    shell.Close()
                evt.Skip()
            frame.Bind(wx.EVT_CLOSE, CloseShell)
                    
        return True


    def OnExitApp(self, evt):
        self.frame.Close(True)


    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "Shutdown"):
            self.window.Shutdown()
        evt.Skip()


    def OnHelpAbout(self, event):
        from aboutDialog import MyAboutBox
        about = MyAboutBox(self.window)
        about.ShowModal()
        about.Destroy()


#----------------------------------------------------------------------------


def main():
    if config.debug: print "wx.version:", wx.version()
    if config.debug: print "pid:", os.getpid()

    args = sys.argv[1:]

    from collective.buildout.cluster import Cluster

    if (len(args) == 0) and os.path.exists('buildout.cfg'):
        config_file = 'buildout.cfg'
        installed_file = '.installed.cfg'
    elif (len(args) == 1) and os.path.exists(args[0]):
        config_file = args[0]
        installed_file = '.installed.cfg'
    elif (len(args) == 2):
        config_file = args[0]
        installed_file = args[1]
    else:
        print "Usage: controller.py <config-file>\n" \
                     "Where <config-file> is the buildout configuration file"
        sys.exit(1)

    cluster = Cluster(os.path.dirname(config_file), config_file, installed_file)
    config.setCluster(cluster)
    useShell = os.environ.has_key('USE_SHELL')
    app = RunApp(os.getcwd(), Notebook, useShell, cluster)
    app.MainLoop()


if __name__ == "__main__":
    main()


