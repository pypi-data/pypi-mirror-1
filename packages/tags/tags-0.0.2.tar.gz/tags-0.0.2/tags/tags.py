#!/usr/bin/env python

from abc import ABCMeta, abstractmethod, abstractproperty
import cgi
import pdb

smallstandardattributes = ['class', 'id', 'style', 'title']
coreattributes = ['class', 'id', 'style', 'title']
languageattributes = ['dir', 'lang']
keyboardattributes = ['accesskey', 'tabindex']

standardattributes = ['class', 'dir', 'id', 'lang', 'style', 'title']

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

class TagException(Exception):
    pass

class TypeError(TagException):
    pass

class OptionError(TagException):
    pass

class NotSupported(TagException):
    pass

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
        return self
    
    @abstractmethod
    def setattrs(self, **kargs):
        classunrename(kargs)
        allowedattrs = self.allowedattrs + self.requiredattrs
        # check for required attributes
        for attr in self.requiredattrs:
            if (not attr in kargs) and (not attr in self.attrs):
                raise TypeError('Tag requires an obligatory attribute %s' % attr)
        
        # check if all attributes are allowed
        for arg in kargs:
            if arg not in allowedattrs:
                raise TypeError("Attribute %s doesn't exist for Tag" % arg)
            if not isinstance(kargs[arg], str):
                raise TypeError("Attribute content of %s must be a str" % arg)
        self.attrs.update(kargs)
        return self
        
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
    
    def configure(self, option, value):
        if not option in ["noindent"]:
            raise OptionError
        setattr(self, option, value)
        return self

class Doctype(Tag):
    def __init__(self):
        self.attrs = {}
        self.children = []
        self.allowedattrs = []
        self.requiredattrs = []
        self.noindent = False
        
    def setattrs(self, **kargs):
        raise NotSupported("Doctype does not allow attributes")
        return self
    
    def append(self, *tags):
        Tag.append(self, *tags, type=IDoctypeChild)
        return self
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='doctype'):
        ret = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'+newline
        content = ''.join([c.render(indentlevel=indentlevel,
                indentstr=indentstr,
                newline=newline,
                content=None
                ) for c in self.children])
        return ret + content

class Html(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.children = []
        self.allowedattrs = ['dir','lang','xml:lang']
        self.requiredattrs = []
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
        self.requiredattrs = []
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
        self.requiredattrs = []
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
    # TODO only allow head followed by body
    def __init__(self, **kargs):
        self.attrs = {}
        self.children = []
        self.allowedattrs = standardattributes
        self.requiredattrs = []
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
        self.requiredattrs = []
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
        self.requiredattrs = []
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
        self.requiredattrs = []
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
        self.requiredattrs = []
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
        self.requiredattrs = []
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
        self.requiredattrs = []
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
        self.requiredattrs = []
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
        self.requiredattrs = []
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
        self.requiredattrs = []
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
        self.requiredattrs = []
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

class Span(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.requiredattrs = []
        self.allowedattrs = standardattributes
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=ISpanChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='span'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)
        
        
class Applet(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = smallstandardattributes
        self.allowedattrs += ['align', 'alt', 'archive', 'codebase', 'height',
                              'hspace', 'name', 'vspace', 'width']
        self.requiredattrs = ['code', 'object']
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=IAppletChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='applet'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)
   
class Textarea(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = standardattributes + ['tabindex', 'accesskey']
        self.allowedattrs += ['disabled', 'name', 'readonly']
        self.requiredattrs = ['cols', 'rows']
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=ITextareaChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='textarea'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)
    
class Img(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = standardattributes
        self.allowedattrs += ['ismap', 'longdesc']
        self.requiredattrs = ['alt', 'src']
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=IImgChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='img'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)

class Address(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = standardattributes
        self.allowedattrs += []
        self.requiredattrs = []
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=IAddressChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='address'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)

class Blockquote(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = standardattributes
        self.allowedattrs += ['cite']
        self.requiredattrs = []
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=IBlockquoteChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='blockquote'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)

class Center(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = smallstandardattributes + ['dir', 'lang']
        self.allowedattrs += []
        self.requiredattrs = []
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=ICenterChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='center'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)

class P(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = standardattributes
        self.allowedattrs += []
        self.requiredattrs = []
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=IPChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='p'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)

class Pre(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = standardattributes
        self.allowedattrs += []
        self.requiredattrs = []
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=IPreChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='pre'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)

class Dir(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = standardattributes
        self.allowedattrs += []
        self.requiredattrs = []
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        Tag.append(self, *tags, type=IDirChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='dir'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)

class Li(Tag):
    def __init__(self, **kargs):
        self.attrs = {}
        self.allowedattrs = standardattributes
        self.allowedattrs += []
        self.requiredattrs = []
        self.children = []
        self.setattrs(**kargs)
        self.noindent = False
    
    def append(self, *tags):
        # TODO distinguish between Li in dir/menu and dir in ol/ul
        Tag.append(self, *tags, type=ILiChild)
        return self
    
    def setattrs(self, **kargs):
        Tag.setattrs(self, **kargs)
    
    def render(self, indentlevel=0, indentstr='  ', newline='\n', content=None,
               tagname='dir'):
        return Tag.render(self, indentlevel, indentstr, newline, content, tagname)

class IBodyChild:
    __metaclass__ = ABCMeta

IBodyChild.register(Div)
IBodyChild.register(Text)
IBodyChild.register(Form)
IBodyChild.register(Hr)
IBodyChild.register(Table)
IBodyChild.register(Br)
IBodyChild.register(Span)
IBodyChild.register(Applet)
IBodyChild.register(P)

class IDivChild:
    __metaclass__ = ABCMeta
    
IDivChild.register(Div)
IDivChild.register(Text)
IDivChild.register(A)
IDivChild.register(Br)
IDivChild.register(Table)
IDivChild.register(Hr)
IDivChild.register(Span)
IBodyChild.register(Applet)

class ISpanChild:
    __metaclass__ = ABCMeta
    
ISpanChild.register(Div)
ISpanChild.register(Text)
ISpanChild.register(A)
ISpanChild.register(Br)
ISpanChild.register(Table)
ISpanChild.register(Hr)
ISpanChild.register(Div)
IBodyChild.register(Applet)

class IFormChild:
    __metaclass__ = ABCMeta
    
IFormChild.register(Div)
IFormChild.register(Span)
IFormChild.register(Text)
IFormChild.register(Table)
IBodyChild.register(Applet)

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
IBodyChild.register(Applet)

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

class IDoctypeChild:
    __metaclass__ = ABCMeta
    
IDoctypeChild.register(Html)

class IAppletChild:
    __metaclass__ = ABCMeta
    
IAppletChild.register(Text)
# TODO [Block-Elemente] | [Inline-Elemente] | param

class ITextareaChild:
    __metaclass__ = ABCMeta
    
ITextareaChild.register(Text)

class IImgChild:
    __metaclass__ = ABCMeta
# img doesn't allow children

class IAddressChild:
    __metaclass__ = ABCMeta

# TODO [Inline-Elemente] | p
IAddressChild.register(P)

class IBlockquoteChild:
    __metaclass__ = ABCMeta

# TODO    #PCDATA und [Block-Elemente] | [Inline-Elemente]
IBlockquoteChild.register(Text)

class ICenterChild:
    __metaclass__ = ABCMeta

# TODO  [Block-Elemente] | [Inline-Elemente]  
ICenterChild.register(Text)
ICenterChild.register(P)

class IPChild:
    __metaclass__ = ABCMeta

# TODO #PCDATA [Inline-Elemente]
IPChild.register(Text)

class IPreChild:
    __metaclass__ = ABCMeta

# TODO #PCDATA a | abbr | acronym | applet | b | bdo | br | button | cite | code |
#   dfn | em | i | input | iframe | kbd | label | map | q | samp | script | select |
#   span | strong | textarea | tt | var
IPChild.register(Text)

class IDirChild:
    __metaclass__ = ABCMeta
    
IDirChild.register(Li)

class ILiChild:
    __metaclass__ = ABCMeta
    
# TODO
ILiChild.register(Text)