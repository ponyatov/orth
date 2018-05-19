# **ORTH**odoxal (meta)programming language
## how to design metaprogramming system from scratch

(c) Dmitry Ponyatov <dponyatov@gmail.com>

github: https://github.com/ponyatov/orth

### see more in manual: https://github.com/ponyatov/orth/wiki

What we want to have is some interactive system able to let us
construct software in high-level terms like data flows, deploy schemes, 
generic objects like queues, stacks, objects, databases, use cases and so on.
And there is one thing was not understood by many many experimental and 
orthodoxal programming language designers: _language manual must be 
**implementation manual** guides the user toward his own implementation of 
the same language_. The key is no one experimental language can't contend 
with mainstream leaders like C++, Java, Python and HTML/JS Web domain. 
And it is not required: **new language must complement them in symbiosis**.

This tiny demo is about implementing tiny [[FORTH]]-inspired script language 
system for [[metaprogramming]]. The idea is about making some ultra high-level 
system lets 
* to describe templates of software design in generic terms, objects, 
algorithm specifications, 
* and generate source code for wide range of target mainstream languages 
and runtime environments (OSes, frameworks, platroms,..)
* finally, the proof of concept is a _metacircular description of metasystem_ 
itself allows to bootstrap in portable and transparent way

The base for the bootstrap process is tiny virtual machine written in Python. 
It is minimalistic for porting simplicity, and these Wiki pages describe 
most parts of it to let you reimplement it yourself in a way you want.
I purposely removed many of the complicated things described in the 
[larger project](http://ponyatov.github.io/o/) to highlight a few key elements, 
and do not overload the implementation with details.
