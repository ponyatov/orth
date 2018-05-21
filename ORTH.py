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
def INTERPRET(SRC=''): print SRC
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
## file/save callback
def onSave(event):
    FileName = main.GetTitle()
    F = open(FileName,'w')
    F.write(editor.GetValue())
    F.close()
main.Bind(wx.EVT_MENU,onSave,save)

## file/quit
quit = file.Append(wx.ID_EXIT,'&Quit')
main.Bind(wx.EVT_MENU,lambda e:main.Close(),quit)

## debug submenu
debug = wx.Menu() ; menubar.Append(debug,'&Debug')

## debug/stack
stack = debug.Append(wx.ID_ANY,'&Stack\tF9',kind=wx.ITEM_CHECK)

## debug/words
words = debug.Append(wx.ID_ANY,'&Words\tF8',kind=wx.ITEM_CHECK)

## help submenu
help = wx.Menu() ; menubar.Append(help,'&Help')

## help/about
about = help.Append(wx.ID_ABOUT,'&About\tF1')
## about event callback
def onAbout(event):
    AboutFile = open('README.md')
    # we need only first 8 lines
    info = AboutFile.readlines()[:8]
    # functional hint to convert list to string
    info = reduce(lambda a,b:a+b,info)
    AboutFile.close()
    # display (modal) message box
    wx.MessageBox(info,'About',wx.OK|wx.ICON_INFORMATION)
main.Bind(wx.EVT_MENU,onAbout,about)

## script editor widget
editor = wx.stc.StyledTextCtrl(main)

## load default editor script
def defaultScriptLoad(SrcFileName = sys.argv[0]+'.src'):
    main.SetTitle(SrcFileName)
    F = open(SrcFileName)
    editor.SetValue(F.read())
    F.close()
defaultScriptLoad()

## key press callback
def onKey(event):
    char = event.GetKeyCode()   # char code
    ctrl = event.CmdDown()      # Ctrl key
    shift = event.ShiftDown()   # Shift key
    if char == 13 and ( ctrl or shift ): # Ctrl-Enter
        Q.put(editor.GetSelectedText())  # push FORTH request
    else: event.Skip()
editor.Bind(wx.EVT_CHAR,onKey)

## GUI/FORTH interfacing queue
Q = Queue.Queue()

## interpreter queue processing thread
class Interpreter(threading.Thread):
    ## expand `threading.Thread` with stop flag
    def __init__(self):
        threading.Thread.__init__(self)
        ## stop flag
        self.stop = False
    ## timeouted loop over Q requests 
    def run(self):
        while not self.stop:
            try: INTERPRET(Q.get(timeout=1))
            except Queue.Empty: pass

## interpreter background thread            
interpreter = Interpreter() ; interpreter.start()

app.MainLoop()      # start GUI event processing loop

## stop flag
interpreter.stop = True     # raise stop flag
interpreter.join()          # wait until interpreter thread stops

## @}
