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

import wx           # wxPython
import wx.stc       # editor extension

import threading    # we need a separate thread for the interpreter
import Queue        # and the queue to send commands from GUI

## wxPython application
app = wx.App()

## @defgroup editor Editor
## simple FORTH code editor with syntax highlight and vocabulary completion
## @{

## @defgroup keys Keys 
## @brief key bindings

## @defgroup colorizer Colorizer
## @brief syntax colorizer using PLY lex/yacc library
## @{

## @defgroup parser FORTH parser
## @brief Syntax parser using PLY library
## @{

import ply.lex as lex

## colorizer token types
tokens = ['ANY','COMMENT','NUMBER','COMPILER','OPERATOR']

## ignore spaces
t_ignore = ' \t\r\n'

## comment
t_COMMENT = r'[\#\\].*\n|\(.*\)'
## number
t_NUMBER = r'0x[0-9A-Fa-f]+|[\+\-]?[0-9]+(\.[0-9]*)?([eE][\+\-]?[0-9]+)?'
## word name or undefined
t_ANY = r'[a-zA-Z0-9_]+'
## compiler words
t_COMPILER = r'[\:\;]{1}'
## operators
t_OPERATOR = r'[\<\>\?\=]'

## lexer error callback
def t_error(t): raise SyntaxError(t)

## FORTH coloring lexer
lexer = lex.lex()

## @}

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
        self.Bind(wx.EVT_MENU,self.onQuit,self.quit)
        
        ## debug submenu
        self.debug = wx.Menu() ; self.menubar.Append(self.debug,'&Debug')
        ## debug/update
        self.update = self.debug.Append(wx.ID_REFRESH,'&Update\tF12')
        self.Bind(wx.EVT_MENU,self.onUpdate,self.update)
        ## debug/stack menu item
        ## @ingroup debug
        self.stack = self.debug.Append(wx.ID_ANY,'&Stack\tF9',kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU,self.onStack,self.stack)
        ## debug/words menu item
        ## @ingroup debug
        self.words = self.debug.Append(wx.ID_ANY,'&Words\tF8',kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU,self.onWords,self.words)
        
        ## help submenu
        self.help = wx.Menu() ; self.menubar.Append(self.help,'&Help')
        ## help/about
        self.about = self.help.Append(wx.ID_ABOUT,'&About\tF1')
        self.Bind(wx.EVT_MENU,self.onAbout,self.about)
    ## init editor
    ## @ingroup keys
    def initEditor(self):
        ## script editor widget
        ## @ingroup editor
        self.editor = wx.stc.StyledTextCtrl(self)
        ## init colorizer
        self.initColorizer()
        ## load default file name
        self.onLoad(None)
        ## bind keys
        self.editor.Bind(wx.EVT_CHAR,self.onKey)
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
        try: F = open(self.filename) ; self.editor.SetValue(F.read()) ; F.close()
        except IOError: pass
    
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
        ## operator
        self.style_OPERATOR = 4
        self.editor.StyleSetSpec(self.style_OPERATOR,'fore:#008888,bold')
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
            elif token.type == 'OPERATOR':
                self.editor.SetStyling(len(token.value),self.style_OPERATOR)
            else:
                self.editor.SetStyling(0,0)
                
    ## toggle stack window callback
    def onStack(self,event):
        if wnStack.IsShown():   wnStack.Hide()
        else:                   wnStack.Show() ; self.onUpdate(event)
    ## toggle vocabulary window callback
    def onWords(self,event):
        if wnWords.IsShown():   wnWords.Hide()
        else:                   wnWords.Show() ; self.onUpdate(event)

    ## process quit event
    def onQuit(self,event):
        wnStack.Close() ; wnWords.Close() ; wnMain.Close()
        
    ## run update process (debug windows only)
    def onUpdate(self,event):
        if (wnStack.editor.IsShown()):
            S = ''
            for i in D: S += '%s\n'%i
            wnStack.editor.SetValue(S)
        if (wnWords.editor.IsShown()):
            S = ''
            for j in W: S += '%s = %s\n'%(j,W[j])
            wnWords.editor.SetValue(S)
            
    ## key press callback
    ## @ingroup keys
    def onKey(self,event):
        char = event.GetKeyCode()   # char code
        ctrl = event.CmdDown()      # Ctrl key
        shift = event.ShiftDown()   # Shift key
        if char == 13 and ( ctrl or shift ):    # Ctrl-Enter
            Q.put(self.editor.GetSelectedText())# push FORTH request
        else: event.Skip()
        
## @}

## main window
wnMain = Editor(filename = sys.argv[0]+'.src') ; wnMain.Show()

## stack dump window
## @ingroup debug
wnStack = Editor(wnMain,filename = sys.argv[0]+'.stack')

## vocabulary dump window
## @ingroup debug
wnWords = Editor(wnMain,filename = sys.argv[0]+'.words')

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
