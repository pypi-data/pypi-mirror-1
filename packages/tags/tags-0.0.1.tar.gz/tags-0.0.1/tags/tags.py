#!/usr/bin/env python

from abc import ABCMeta, abstractmethod, abstractproperty
import cgi
import pdb

standardattributes = ['class', 'dir', 'ltr', 'id', 'lang', 'style', 'title',
                      'xml:lang']

def renderstarttag(tagname, **attrs):
    def quote(value):
        return '"{0}"'.format(value)
    if len(attrs) == 0:
        return "<{name}>".format(name=tagname)
    astr = " ".join(['='.join([e,quote(attrs[e])]) for e in attrs])
    return "<{name} {astr}>".format(name=tagname, astr=astr)

def renderendtag(name):
    return "</{0}>".format(name)

def classunrename(dict):
    if dict.has_key('klass'):
        dict['class'] = dict['klass']
        del dict['klass']

class Tag:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def render(self, indentlevel, indentstr, newline, content, tagname):
        fmtstr = "{indent}{stag}{content}{indent}{etag}"
        indent =  newline + (indentstr * indentlevel)
        if self.noindent:
            fmtstr = "{indent}{stag}{content}{etag}"
            indentstr = ''
            newline = ''
        if content == None:
            content = ''.join([c.render(indentlevel=indentlevel+1,
                          indentstr=indentstr,
                          newline=newline,
                          content=None
                         ) for c in self.children])
        return fmtstr.format(indent=indent,
                          stag=renderstarttag(tagname, **self.attrs),
                          etag=renderendtag(tagname),
                          content=content)
    
    @abstractmethod
    def setattrs(self, **kargs):
        classunrename(kargs)
        for arg in kargs:
            if arg not in self.allowedattrs:
                raise TypeError("Attribute %s doesn't exist for Tag" % arg)
            if not isinstance(kargs[arg], str):
                raise TypeError("Attribute content of %s must be a str" % arg)
        self.attrs.update(kargs)
        
    @abstractmethod
    def append(self, *tags, **kargs):
        if kargs.has_key('type'):
            type = kargs['type']
        else:
            # No type checking
            self.children.extend(tags)
        for tag in tags:
            if not isinstance(tag, type):
                #tagtype = type(tag)
                tagtype = 'unknown' #TODO
                raise TypeError('Tag was of type %s. Expected %s.' %
                                (tagtype,type))
        else:
            self.children.extend(tags)

class TypeError(Exception):
    pass

class Html(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.children = []
        self.allowedattrs = ['dir','lang','xml:lang']
        self.setattrs(**kargs)
        self.noindent = False
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)

    def append(self, *tags):
        Tag.append(self, *tags, type=IHtmlChild)
        return self
    
    def render(self, indentlevel=0, indentstr='  ',
               newline='\n', content=None, tagname='html'):
        return Tag.render(self,indentlevel,indentstr,newline,content=content,
                          tagname=tagname)
        
class Head(Tag):
    #<base>, <link>, <meta>, <title>, <style>, and <script> 
    def __init__(self, **kargs):
        self.attrs = {}
        self.children = []
        self.allowedattrs = standardattributes
        self.setattrs(**kargs)
        self.noindent=False
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)

    def append(self, *tags):
        Tag.append(self, *tags, type=IHeadChild)
        return self
    
    def render(self, indentlevel=0, indentstr='  ',
               newline='\n', content=None, tagname='head'):
        
        content = ''.join([c.render(indentlevel=indentlevel+1,
                          indentstr=indentstr,
                          newline=newline,
                          content=None
                         ) for c in self.children])
        
        return Tag.render(self,indentlevel,indentstr,newline,content=content,
                          tagname='head')

class Text(Tag):
    def __init__(self, text=''):
            self.text = text
            self.noindent=False
    
    def setattrs(self, **kargs):
        raise Exception("setattr() not allowed for text")
    
    def append(self, *tags):
        raise Exception("Text has no method append")
    
    def lbreplace(self, str, new):
        return new + str.replace('\n', new)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n',content=None):
        indent = newline + (indentstr * indentlevel)
        return self.lbreplace(cgi.escape(self.text), indent)

class Title(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.children = []
        self.allowedattrs = standardattributes
        self.setattrs(**kargs)
        self.noindent=False
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)

    def append(self, *tags):
        Tag.append(self, *tags, type=ITitleChild)
        return self
    
    def render(self, indentlevel=0, indentstr='  ',
               newline='\n', content=None, tagname='title'):
        return Tag.render(self,indentlevel,indentstr,newline,content=content,
                          tagname=tagname)

class Body(Tag):    
    def __init__(self, **kargs):
        self.attrs = {}
        self.children = []
        self.allowedattrs = standardattributes
        self.setattrs(**kargs)
        self.noindent = False
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)

    def append(self, *tags):
        Tag.append(self, *tags, type=IBodyChild)
        return self
    
    def render(self, indentlevel=0, indentstr='  ',
               newline='\n', content=None, tagname='body'):
        return Tag.render(self,indentlevel,indentstr,newline,content=content,
                          tagname=tagname)

class Link(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.children = []
        self.allowedattrs = ['charset', 'href', 'hreflang', 'media', 'rel',
                             'rev', 'target', 'type']
        self.allowedattrs.extend(standardattributes)
        self.setattrs(**kargs)
        self.noindent=False
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def append(self, *tags):
        raise TypeError("Appending not allowed for <link> tag")
        return self
    
    def render(self, indentlevel=0, indentstr='  ',
               newline='\n', content=None, tagname='link'):
        indent =  newline + (indentstr * indentlevel)
        return indent+renderstarttag('link', **self.attrs)

class A(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.children = []
        self.allowedattrs = ['href', 'charset', 'coords', 'hreflang', 'name',
                             'rel', 'rev', 'shape', 'target']
        self.allowedattrs.extend(standardattributes)
        self.setattrs(**kargs)
        self.noindent = False
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def append(self, *tags):
        Tag.append(self, *tags, type=IAChild)
        return self
    
    def render(self, indentlevel=0, indentstr='  ',
               newline='\n', content=None, tagname='a'):
        return Tag.render(self,indentlevel,indentstr,newline,content=content,
                          tagname=tagname)

class Input(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.children = []
        self.allowedattrs = ['accept', 'alt', 'checked', 'disabled', 'maxlength',
                             'name', 'readonly', 'size', 'src', 'type', 'value']
        self.allowedattrs.extend(standardattributes)
        self.setattrs(**kargs)
        self.noindent = False
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def append(self, tag):
        raise TypeError("Appending not allowed for <input> tag")
        return self
    
    def render(self, indentlevel=0, indentstr='  ',
               newline='\n', content=None, tagname='input'):
        indent =  newline + (indentstr * indentlevel)
        return indent+renderstarttag(tagname, **self.attrs)

class Form(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.children = []
        self.allowedattrs = ['method', 'action'] + standardattributes
        self.setattrs(**kargs)
        self.noindent = False
        
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def append(self, *tags):
        Tag.append(self, *tags, type=IFormChild)
        return self
    
    def render(self, indentlevel=0, indentstr='  ',
               newline='\n', content=None, tagname='form'):
        return Tag.render(self,indentlevel,indentstr,newline,content=content,
                          tagname=tagname)

class Table(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = ['border','cellpadding','cellspacing','frame',
                             'rules', 'summary', 'width']
        self.allowedattrs.extend(standardattributes)
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=ITableChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='table'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)

class Tr(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = ['align','char','charoff','valign']
        self.allowedattrs.extend(standardattributes)
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=ITrChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='tr'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)    

class Td(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = ['abbr','align','axis','char','charoff','colspan',
                             'headers', 'height', 'rowspan', 'scope', 'valign'
                             ]
        self.allowedattrs.extend(standardattributes)
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=ITdChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='td'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)

class Div(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = standardattributes
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=IDivChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='div'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)

class Hr(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.children = []
        self.allowedattrs = standardattributes
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, tag):
        raise TypeError("Appending not allowed for <hr> tag")
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='hr'):
        indent =  newline + (indentstr * indentlevel)
        return indent+renderstarttag('hr', **self.attrs)

class Br(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.children = []
        self.allowedattrs = ['class', 'id', 'style', 'title']
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, tag):
        raise TypeError("Appending not allowed for <br> tag")
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='br'):
        indent =  newline + (indentstr * indentlevel)
        return indent+renderstarttag('br', **self.attrs)

class IBodyChild:
    __metaclass__ = ABCMeta

IBodyChild.register(Div)
IBodyChild.register(Text)
IBodyChild.register(Form)
IBodyChild.register(Hr)
IBodyChild.register(Table)
IBodyChild.register(Br)

class IDivChild:
    __metaclass__ = ABCMeta
    
IDivChild.register(Div)
IDivChild.register(Text)
IDivChild.register(A)
IDivChild.register(Br)
IDivChild.register(Table)
IDivChild.register(Hr)

class IFormChild:
    __metaclass__ = ABCMeta
    
IFormChild.register(Div)
IFormChild.register(Text)
IFormChild.register(Table)

class IAChild:
    __metaclass__ = ABCMeta

IAChild.register(Text)

class ITableChild:
    __metaclass__ = ABCMeta
    
ITableChild.register(Tr)

class ITrChild:
    __metaclass__ = ABCMeta
    
ITrChild.register(Td)

class ITdChild:
    __metaclass__ = ABCMeta
    
ITdChild.register(Text)
ITdChild.register(Input)
ITdChild.register(Div)
ITdChild.register(Br)
ITdChild.register(A)

class IHeadChild:
    __metaclass__ = ABCMeta
#<base>, <link>, <meta>, <title>, <style>, and <script> 
#IHeadChild.register(Base)
IHeadChild.register(Link)
#IHeadChild.register(Meta)
IHeadChild.register(Title)
#IHeadChild.register(Style)
#IHeadChild.register(Script)

class ITitleChild:
    __metaclass__ = ABCMeta

ITitleChild.register(Text)

class IHtmlChild:
    __metaclass__ = ABCMeta
    
class IHtmlChild:
    __metaclass__ = ABCMeta

IHtmlChild.register(Body)
IHtmlChild.register(Head)



#def print_login_form():
#    body=Body().append(Menu())
#    #leftmenu = Div(style="float:left").append(A(href='/home').append(Text('Home')))
#    #leftmenu.append(A(href='list').append(Text('List')))
#    #body = Body().append(leftmenu)
#    #body.append(Hr(style="width=100%; color: #3333cc; background-color: #3333cc;"))
#    #form = Form(method="post")
#    #table = Table(klass="loginbox")
#    #row1 = Tr()
#    #col1 = Td()
#    #col2 = Td()
#    #row1.append(col1).append(col2)
#    #table.append(row1)
#    #form.append(table)
#    #body.append(form)
#    body.append(LoginBox())
#    head = Head().append(Title().append(Text('Voting Tool')))
#    head.append(Link(rel="stylesheet", type="text/css", href="static/css/default.css", media="all"))
#    h = Html().append(head).append(body)
#    print h.render()
##    
##body = Body(id="mybody", klass="blha")
##body.append(Div(id="yahoo"))
##form = Form(method="post", action="./")
##body.append(form)
##t = Text("Blah\n Yahoo\nfjasdk")
###print t.render()
##body.append(Text("Blah\nsfksfd"))
### body.append(Td())
##head = Head().append(Title().append(Text('Hallo Welt')))
##h = Html(head, body)    
#    
## print_login_form()
#
#print Site().respond()
#
##print h.render()
##print renderstarttag('html',style="blah")