## @file
## ORTH concept language demo implementation in Python
## @author (c) Dmitry Ponyatov <<dponyatov@gmail.com>>
## 
## github: https://github.com/ponyatov/orth
##
## manual: https://github.com/ponyatov/orth/wiki/ORTH

## vocabulary
W = {}
# data stack
D = []  

def q(): print D
W['?'] = q

def qq(): print W
W['??'] = qq

def INTERPRET():
    pass
W['INTERPRET'] = INTERPRET
