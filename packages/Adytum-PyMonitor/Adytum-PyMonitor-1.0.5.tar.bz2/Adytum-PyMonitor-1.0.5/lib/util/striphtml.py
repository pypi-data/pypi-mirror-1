#!/usr/bin/python

import sgmllib, string

class StrippingParser(sgmllib.SGMLParser):
    
    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib
    
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = [] 
        
    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)
        
    def handle_entityref(self, name):
        if self.entitydefs.has_key(name): 
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''
        self.result = "%s&%s%s" % (self.result, name, x)

    valid_tags = ('b', 'a', 'i', 'br', 'p')
    
    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:       
            self.result = self.result + '<' + tag
            for k, v in attrs:
                if string.lower(k[0:2]) != 'on' and string.lower(v[0:10]) != 'javascript':
                    self.result = '%s %s="%s"' % (self.result, k, v)
            endTag = '</%s>' % tag
            self.endTagList.insert(0,endTag)    
            self.result = self.result + '>'
                
    def unknown_endtag(self, tag):
        if tag in self.valid_tags:
            self.result = "%s</%s>" % (self.result, tag)
            remTag = '</%s>' % tag
            self.endTagList.remove(remTag)

    def cleanup(self):
        """ Append missing closing tags """
        for j in range(len(self.endTagList)):
                self.result = self.result + self.endTagList[j]    
        
def strip(s):
    parser = StrippingParser()
    parser.feed(s)
    parser.close()
    parser.cleanup()
    return parser.result
    
if __name__=='__main__':
    text = """<HTML>
<HEAD><TITLE> New Document </TITLE>
<META NAME="Keywords" CONTENT=""></HEAD>
<BODY BGCOLOR="#FFFFFF">
<h1> Hello! </h1>
<a href="index.html" align="left" ONClick="window.open()">index.html</a>
<p>This is some <B><B><B name="my name">this is<I> a simple</I> text</B>
<a><a href="JAVascript:1/0">link</a>.
</BODY></HTML>"""
    print text
    print "==============================================="
    print strip(text)
