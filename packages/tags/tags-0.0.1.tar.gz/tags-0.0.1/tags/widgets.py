#!/usr/bin/env python

from tags import *

class LoginBox(Div):
    def __init__(self):
        Div.__init__(self)
        
        self.setattrs(style="width:98%; margin:1%;")
        
        table = Table(klass="loginbox")
        self.append(table)
        row1 = Tr()
        row2 = Tr()
        row3 = Tr()
        row4 = Tr()
        
        col11 = Td(colspan="2")
        col11.append(Text('Please sign in')).append(Br())
        col11.append(Text('If you have no account '))
        col11.append(A(href="register").append(Text('register')))
        row1.append(col11)
        
        col21 = Td()
        col22 = Td()
        
        col21.append(Div(style="text-align: right;").append(Text('username')))
        col22.append(Input(type="text", name="username"))
        row2.append(col21).append(col22)
        
        col31 = Td()
        col32 = Td()
        col31.append(Div(style="text-align: right").append(Text('password')))
        col32.append(Input(type="password", name="password"))
        row3.append(col31).append(col32)
        
        row4.append(Td()).append(Td().append(Input(type="submit", value="login")))
        
        table.append(row1).append(row2).append(row3).append(row4)

class SimpleMenu(Div):
    class LeftMenu(Div):
        def __init__(self):
            Div.__init__(self)
            self.setattrs(style="float:left;")
            #self.append(A(href="home/").append(Text("home")))
            #self.append(A(href="list/").append(Text("list")))
        def append(self, *tuples):
            """Appends entries to the menu. Every Entry is a tuple containing
            the link and the Text"""
            for e in tuples:
                link, text = e
                appendee = A(href=link).append(Text(text))
                appendee.noindent = True
                Div.append(self, appendee)

    class RightMenu(Div):
        def __init__(self):
            Div.__init__(self)
            self.setattrs(style="float:right;")
            #self.append(Text("patricksabin@gmx.at"))
            #self.append(A(href="login/").append(Text("Login")))
        
        def append(self, *tuples):
            """Appends entries to the menu. Every Entry is a tuple containing
            the link and the Text"""
            for e in tuples:
                link, text = e
                Div.append(self,A(href=link).append(Text(text)))
            
    def __init__(self):
        Div.__init__(self)
        self.right = SimpleMenu.RightMenu()
        self.left = SimpleMenu.LeftMenu()
        self.append(self.left)
        self.append(self.right)
        self.append(Div(style="clear: both;"))
        self.append(Hr(style="width=100%; color: #3333cc; background-color: #3333cc;"))
 
class SimpleTable(Table):
    def __init__(self, namespace={}):
        Table.__init__(self)
        self.make(**namespace)
    
    def make(self, rows, cols, **kargs):
        self.setattrs(**kargs)
        self.rows = []
        self.cols = []
        for n in range(rows):
            self.cols.append([])
            row = Tr()
            self.append(row)
            self.rows.append(row)
            for k in range(cols):
                col = Td()
                self.cols[n].append(Td())
                row.append(col)
                
 
class Pollresult(Table):
    def __init__(self, namespace={}):
        Table.__init__(self)
        self.make(**namespace)
    
    def make(self, polltext, rows, **kargs):
        self.setattrs(klass="mybox")
        headerrow = Tr().append(Td(colspan="2").append(Text(polltext)))
        #TODO
        self.append(headerrow)
        
class StandardHtmlTemplate(Html):
    def __init__(self, namespace={'title':''}):
        Html.__init__(self)
        self.make(**namespace)
        
    def make(self, title, **kargs):
        self.head = Head().append(Title().append(Text(title)))
        self.body = Body()
        self.append(self.head)
        self.append(self.body)