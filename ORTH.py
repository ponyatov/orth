## @file
## ORTH concept language demo implementation in Python
## @author (c) Dmitry Ponyatov <<dponyatov@gmail.com>>
## 
## github: https://github.com/ponyatov/orth
##
## manual: https://github.com/ponyatov/orth/wiki/ORTH

import os,sys

## @defgroup vm Virtual Machine
## @{

## vocabulary
W = {}

## data stack
D = []

## @defgroup debug Debug
## @{

## `? ( -- )` print data stack
def q(): print D
W['?'] = q

## `WORSS ( -- )` print vocabulary
def WORDS(): print W
W['WORDS'] = WORDS

## `?? ( -- )` print full system state including vocabulary
def qq(): WORDS(); q()
W['??'] = qq

## @}

## @defgroup compiler Interpreter
## @{

## interpreter
def INTERPRET(): pass
W['INTERPRET'] = INTERPRET

## @}

## @}

## @defgroup gui GUI
## @{

import wx           # wxPython
import wx.stc       # editor extension

import threading    # we need a separate thread for the interpreter
import Queue        # and the queue to send commands from GUI

## wxPython application
app = wx.App()

## main window
main = wx.Frame(None,title=str(sys.argv)) ; main.Show()

## main window menu
menubar = wx.MenuBar() ; main.SetMenuBar(menubar)

## file submenu
file = wx.Menu() ; menubar.Append(file,'&File')

## file/save
save = file.Append(wx.ID_SAVE,'&Save')

## file/quit
quit = file.Append(wx.ID_EXIT,'&Quit')
main.Bind(wx.EVT_MENU,lambda e:main.Close(),quit)

## debug submenu
debug = wx.Menu() ; menubar.Append(debug,'&Debug')

## debug/stack
stack = debug.Append(wx.ID_ANY,'&Stack',kind=wx.ITEM_CHECK)

## debug/words
words = debug.Append(wx.ID_ANY,'&Words',kind=wx.ITEM_CHECK)

## help submenu
help = wx.Menu() ; menubar.Append(help,'&Help')

## help/about
about = help.Append(wx.ID_ABOUT,'&About\tF1')
## about event callback
def onAbout(event):
    AboutFile = open('README.md')
    info = AboutFile.readlines()[:8]
    # functional hint to convert list to string
    info = reduce(lambda a,b:a+b,info)
    AboutFile.close()
    wx.MessageBox(info)
main.Bind(wx.EVT_MENU,onAbout,about)

app.MainLoop()      # start GUI event processing loop

## @}
