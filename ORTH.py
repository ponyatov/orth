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
def qq(): WORDS() ; q()
W['??'] = qq

## @}

## @defgroup interpreter Interpreter
## @{

## interpreter
def INTERPRET(SRC=''): print SRC
W['INTERPRET'] = INTERPRET

## @}

## @}

## @defgroup gui GUI
## @{

## @defgroup editor Editor
## simple FORTH code editor with syntax highlight and vocabulary completion

import wx           # wxPython
import wx.stc       # editor extension

import threading    # we need a separate thread for the interpreter
import Queue        # and the queue to send commands from GUI

## wxPython application
app = wx.App()

## key press callback
## @ingroup editor
def onKey(event):
    char = event.GetKeyCode()   # char code
    ctrl = event.CmdDown()      # Ctrl key
    shift = event.ShiftDown()   # Shift key
    if char == 13 and ( ctrl or shift ): # Ctrl-Enter
        Q.put(editor.GetSelectedText())  # push FORTH request
    else: event.Skip()
# editor.Bind(wx.EVT_CHAR,onKey)

## @defgroup colorizer Colorizer
## @brief syntax colorizer using PLY lex/yacc library
## @{

import ply.lex as lex

## colorizer token types
tokens = ['ANY','COMMENT','NUMBER','COMPILER']

## ignore spaces
t_ignore = ' \t\r\n'

## comment
t_COMMENT = r'[\#\\].*\n|\(.*\)'
## number
t_NUMBER = r'[\+\-]?[0-9]+(\.[0-9]*)?([eE][\+\-]?[0-9]+)?'
## word name or undefined
t_ANY = r'[a-zA-Z0-9_]+'
## compiler words
t_COMPILER = r'[\:\;]{1}'

## lexer error callback
def t_error(t): raise SyntaxError(t)

## FORTH coloring lexer
lexer = lex.lex()

            

# ## stack dump window
# wnstack = wx.Frame(main,title=sys.argv[0]+'.stack')
# ## toggle stack window callback
# def onStack(event):
#     if wnstack.IsShown():   wnstack.Hide()
#     else:                   wnstack.Show()
# ## bind to debug/stack menu
# main.Bind(wx.EVT_MENU,onStack,stack)
# 
# ## vocabulary dump window
# wnwords = wx.Frame(main,title=sys.argv[0]+'.words')
# ## toggle vocabulary window callback
# def onWords(event):
#     if wnwords.IsShown():   wnwords.Hide()
#     else:                   wnwords.Show()
# ## bind to debug/words menu
# main.Bind(wx.EVT_MENU,onWords,words)

## GUI Editor class
## @ingroup editor
class Editor(wx.Frame):
    ## define constructor parameters to default values specific for our app
    def __init__(self,parent=None,filename=sys.argv[0]+'.src'):
        ## use window title = file name to visually bind file/window
        self.filename = filename
        wx.Frame.__init__(self,parent,title=self.filename)
        self.initMenu()
        self.initEditor()
        self.initStatusBar()
    ## init menu
    def initMenu(self):
        ## window menu
        self.menubar = wx.MenuBar() ; self.SetMenuBar(self.menubar)
        
        ## file submenu
        self.file = wx.Menu() ; self.menubar.Append(self.file,'&File')
        ## file/save
        self.save = self.file.Append(wx.ID_SAVE,'&Save')
        self.Bind(wx.EVT_MENU,self.onSave,self.save)
        ## file/quit
        self.quit = self.file.Append(wx.ID_EXIT,'&Quit')
        self.Bind(wx.EVT_MENU,lambda e:self.Close(),self.quit)
        
        ## debug submenu
        self.debug = wx.Menu() ; self.menubar.Append(self.debug,'&Debug')
        ## debug/stack
        ## @ingroup debug
        self.stack = self.debug.Append(wx.ID_ANY,'&Stack\tF9',kind=wx.ITEM_CHECK)
        ## debug/words
        ## @ingroup debug
        self.words = self.debug.Append(wx.ID_ANY,'&Words\tF8',kind=wx.ITEM_CHECK)
        
        ## help submenu
        self.help = wx.Menu() ; self.menubar.Append(self.help,'&Help')
        ## help/about
        self.about = self.help.Append(wx.ID_ABOUT,'&About\tF1')
        self.Bind(wx.EVT_MENU,self.onAbout,self.about)
    ## init editor
    def initEditor(self):
        ## script editor widget
        ## @ingroup editor
        self.editor = wx.stc.StyledTextCtrl(self)
        ## init colorizer
        self.initColorizer()
        ## load default file name
        self.onLoad(None)
    ## init statusbar
    def initStatusBar(self):
        ## statusbar
        self.statusbar = wx.StatusBar(self)
        self.SetStatusBar(self.statusbar)
        
    ## about event callback
    def onAbout(self,event):
        AboutFile = open('README.md')
        # we need only first 8 lines
        info = AboutFile.readlines()[:8]
        # functional hint to convert list to string
        info = reduce(lambda a,b:a+b,info)
        AboutFile.close()
        # display (modal) message box
        wx.MessageBox(info,'About',wx.OK|wx.ICON_INFORMATION)
        
    ## file/save callback
    def onSave(self,event):
        FileName = self.GetTitle() 
        F = open(FileName,'w') ; F.write(self.editor.GetValue()) ; F.close()
        
    ## (re)load file event callback
    ## @ingroup editor
    def onLoad(self,event):
        F = open(self.filename)
        self.editor.SetValue(F.read()) ; F.close()
    
    ## init colorizer styles & lexer
    ## @ingroup colorizer
    def initColorizer(self):
        ## get monospace font from system
        self.font = wx.Font(14, wx.FONTFAMILY_MODERN,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        ## load default editor style
        self.editor.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT,
            "face:%s,size:%d" % (
                self.font.GetFaceName(), self.font.GetPointSize()))
        # configure styles
        ## default style
        self.style_DEFAULT = wx.stc.STC_STYLE_DEFAULT
        self.editor.StyleSetSpec(self.style_DEFAULT,'fore:#000000')
        ## comment
        self.style_COMMENT = 1
        self.editor.StyleSetSpec(self.style_COMMENT,'fore:#0000FF,normal')
        ## number
        self.style_NUMBER = 2
        self.editor.StyleSetSpec(self.style_NUMBER,'fore:#008800')
        ## colon definition
        self.style_COMPILER = 3
        self.editor.StyleSetSpec(self.style_COMPILER,'fore:#FF0000,bold')
        # bind colorizer event
        self.editor.Bind(wx.stc.EVT_STC_STYLENEEDED,self.onStyle)

    ## colorizer  callback
    def onStyle(self,event):
        # feed lexer
        text = self.editor.GetValue() ; lexer.input(text)
        # restart styles
        # editor.StartStyling(0,0xFF) ; editor.SetStyling(len(text),style_DEFAULT)
        # process source code via coloring lexer
        while True:
            token = lexer.token()
            if not token: break
            self.editor.StartStyling(token.lexpos,0xFF)
            if token.type == 'COMMENT':
                self.editor.SetStyling(len(token.value),self.style_COMMENT)
            elif token.type == 'NUMBER':
                self.editor.SetStyling(len(token.value),self.style_NUMBER)
            elif token.type == 'COMPILER':
                self.editor.SetStyling(len(token.value),self.style_COMPILER)
            else:
                self.editor.SetStyling(0,0)

## main window
wnMain = Editor(filename = sys.argv[0]+'.src') ; wnMain.Show()

## @}

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
## @ingroup interpreter
interpreter = Interpreter() ; interpreter.start()

app.MainLoop()      # start GUI event processing loop

## stop flag
interpreter.stop = True     # raise stop flag
interpreter.join()          # wait until interpreter thread stops

## @}
