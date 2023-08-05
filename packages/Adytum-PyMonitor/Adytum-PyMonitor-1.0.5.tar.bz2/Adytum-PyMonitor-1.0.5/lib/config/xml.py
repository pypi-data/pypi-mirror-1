import os
import re

import cElementTree as ElementTree

from base import DictConfig

def getTagName(element):
    try:
        return re.split('[{}]', element.tag)[2]
    except IndexError:
        return element.tag

stripNameSpace = getTagName

def getNameSpace(element):
    try:
        return re.split('[{}]', element.tag)[1]
    except IndexError:
        return None

class XmlBaseConfig(object):
    '''
    '''
    def __init__(self, element, keep_namespace=True):
        self.keep_namespace = keep_namespace
        self._namespace = getNameSpace(element)
        self.tag = ''
        self.fulltag = ''

    def getTagName(self, element):
        if self.keep_namespace:
            return element.tag
        else:
            return getTagName(element)

    def getNameSpaceTag(self, tagname):
        if self._namespace:
            return '{%s}%s' % (self._namespace, tagname)
        else:
            return tagname

    def makeSubElement(self, parent_element):
        # create the subelement where the list will be stored
        subtag_name = '%sList'%self.tag
        if self.keep_namespace:
            subtag = self.getNameSpaceTag(subtag_name)
        else:
            subtag = subtag_name
        self.subtag = subtag

        return parent_element.makeelement(self.subtag, {})        

    def treatListType(self, parent_element):
    
        # create a new/empty subelement where the list will be stored
        subelement = self.makeSubElement(parent_element)

        print parent_element.tag
        print parent_element.getchildren()

        # iterate through all elements with the name that is 
        # currently stored/set in self.fulltag
        for element in parent_element.findall(self.fulltag):
            subelement.append(element)
            if element:
                #self.check(element)
                pass
            elif element.text:
                text = element.text.strip()
                if text: pass
                if isinstance(self, list):
                    self.append(text)
                else:
                    self.update({self.tag: text})
        #parent_element.append(subelement)
        aList = XmlListConfig(subelement, keep_namespace=self.keep_namespace)
        if isinstance(self, list):
            self.append(aList)
        else:
            self.update({self.subtag:aList})
            # the next is for backwards compatibility
            self.update({self.tag:aList})
        self.check(subelement)

    def treatDictType(self, parent_element):
        if parent_element.items():
            attrs = dict(parent_element.items())
            self.update(attrs)

        element = parent_element.find(self.fulltag)
        if element != None:
            text = ''
            data = None
            if element.text:
                #print "has text..."
                text = element.text.strip()
                if text: 
                    if isinstance(self, list):
                        #self.append(
                        pass
                    else:
                        self.update({self.tag: text})
            if not text:
                aDict = XmlDictConfig(element, keep_namespace=self.keep_namespace)
                if element.items():
                    #print "adding attributes..."
                    aDict.update(dict(element.items()))
                data = aDict
            if element:
                self.check(element)
            self.update({self.tag: data})

    def check(self, parent_element):
        # get counts of all the elements at this level
        counts = {}
        for element in parent_element:
            tag = self.getTagName(element)
            count = counts.setdefault(tag,0) + 1
            counts.update({tag:count})

        # anything with a count more than 1 is treated as a list, 
        # everything else is a treated as a dict
        for tag, count in counts.items():
            # set tag names for current iteration
            self.tag = tag
            self.fulltag = self.getNameSpaceTag(tag)
            if count > 1:
                # treat like list
                print "treating like a list..."
                print tag
                self.treatListType(parent_element)
            else:
                # treat like dict
                print "treating like a dict..."
                print tag
                self.treatDictType(parent_element)

class XmlListConfig(XmlBaseConfig, list):
    '''
    '''
    def __init__(self, parent_element, keep_namespace=True):
        list.__init__(self)
        XmlBaseConfig.__init__(self, parent_element, keep_namespace=keep_namespace)

        self.check(parent_element)
            
    def __call__(self, **kw):
        pass

class XmlDictConfig(XmlBaseConfig, dict):
    '''
    '''
    def __init__(self, parent_element, keep_namespace=True):
        dict.__init__(self)
        XmlBaseConfig.__init__(self, parent_element, keep_namespace=keep_namespace)

        if parent_element.items():
            self.update(dict(parent_element.items()))

        self.check(parent_element)

class XmlConfig(DictConfig):
    '''
    # simple test
    >>> xmlstring01 = """<config>
    ... <sub>This is a test</sub>
    ... </config>"""
    >>> cfg = XmlConfig(xmlstring01)
    >>> cfg.sub
    'This is a test'

    # namespace test
    >>> xmlstring01a = """<xml xmlns="http://ns.adytum.us">
    ... <text>Yeay!</text>
    ... <parent><child><grandchild><ggchild>More Yeay!!!</ggchild></grandchild></child></parent>
    ... </xml>"""
    >>> cfg = XmlConfig(xmlstring01a, keep_namespace=False)
    >>> cfg._namespace
    'http://ns.adytum.us'
    >>> stripNameSpace(cfg._root)
    'xml'
    >>> cfg.text
    'Yeay!'
    >>> cfg.parent.child.grandchild.ggchild
    'More Yeay!!!'

    # attributes test
    >>> xmlstring02 = """<config>
    ...   <sub1 type="title" />
    ...
    ...   <sub2 date="now">
    ...     <subsub />
    ...   </sub2>
    ...
    ...   <sub3 quality="high">
    ...     <subsub />
    ...     <subsub />
    ...   </sub3>
    ...
    ...   <sub4 type="title4">
    ...     <subsub1 type="title41">
    ...       <subsub2 type="title42">
    ...         <subsub3 />
    ...         <subsub3 />
    ...       </subsub2>
    ...     </subsub1>
    ...   </sub4>
    ...
    ...   <sub5 type="title5">
    ...     <subsub1 type="title51">
    ...       <subsub2 type="title52">
    ...         <subsub3 />
    ...         <subsub3 />
    ...       </subsub2>
    ...     </subsub1>
    ...     <subsub4 type="title54">
    ...       <subsub5 type="title55">
    ...         <subsub6>something</subsub6>
    ...         <subsub6>another</subsub6>
    ...       </subsub5>
    ...     </subsub4>
    ...   </sub5>
    ... </config>"""
    >>> cfg = XmlConfig(xmlstring02)
    >>> cfg.sub1.type
    'title'
    >>> cfg.sub2.date
    'now'
    >>> cfg.sub3.quality
    'high'
    >>> cfg.sub4.type
    'title4'
    >>> cfg.sub4.subsub1.type
    'title41'
    >>> cfg.sub4.subsub1.subsub2.type
    'title42'
    >>> cfg.sub5.type
    'title5'
    >>> cfg.sub5.subsub1.type
    'title51'
    >>> cfg.sub5.subsub1.subsub2.type
    'title52'
    >>> cfg.sub5.subsub4.type
    'title54'
    >>> cfg.sub5.subsub4.subsub5.type
    'title55'
    >>> cfg.sub5.subsub4.subsub5.subsub6
    ['something', 'another']
    >>> cfg.sub5.subsub4.subsub5.subsub6List
    ['something', 'another']

    # list test
    >>> xmlstring03 = """<config>
    ...   <sub>
    ...     <subsub>Test 1</subsub>
    ...     <subsub>Test 2</subsub>
    ...     <subsub>Test 3</subsub>
    ...   </sub>
    ... </config>"""
    >>> cfg = XmlConfig(xmlstring03)
    >>> for i in cfg.sub.subsub:
    ...   i
    'Test 1'
    'Test 2'
    'Test 3'

    # dict test
    >>> xmlstring04 = """<config>
    ...   <sub1>Test 1</sub1>
    ...   <sub2>Test 2</sub2>
    ...   <sub3>Test 3</sub3>
    ... </config>"""
    >>> cfg = XmlConfig(xmlstring04)
    >>> cfg.sub1
    'Test 1'
    >>> cfg.sub2
    'Test 2'
    >>> cfg.sub3
    'Test 3'

    # deeper structure
    >>> xmlstring05 = """<config>
    ...   <a>Test 1</a>
    ...   <b>Test 2</b>
    ...   <c>
    ...     <ca>Test 3</ca>
    ...     <cb>Test 4</cb>
    ...     <cc>Test 5</cc>
    ...     <cd>
    ...        <cda>Test 6</cda>
    ...        <cdb>Test 7</cdb>
    ...        <cdc>
    ...           <cdca>Test 8</cdca>
    ...        </cdc>
    ...     </cd>
    ...   </c>
    ... </config>"""
    >>> cfg = XmlConfig(xmlstring05)
    >>> cfg.a
    'Test 1'
    >>> cfg.b
    'Test 2'
    >>> cfg.c.ca
    'Test 3'
    >>> cfg.c.cb
    'Test 4'
    >>> cfg.c.cc
    'Test 5'
    >>> cfg.c.cd.cda
    'Test 6'
    >>> cfg.c.cd.cdb
    'Test 7'
    >>> cfg.c.cd.cdc.cdca
    'Test 8'

    # a test that shows possible real-world usage
    >>> xmlstring06 = """<config>
    ...    <services>
    ...        <service type="ping">
    ...            <defaults>
    ...                <ping_count>4</ping_count>
    ...                <service_name>connectivity</service_name>
    ...                <message_template>There was a %s%% ping return from host %s</message_template>
    ...                <ping_binary>/bin/ping</ping_binary>
    ...                <command>ping</command>
    ...                <ok_threshold>67,100</ok_threshold>
    ...                <warn_threshold>26,66</warn_threshold>
    ...                <error_threshold>0,25</error_threshold>
    ...            </defaults>
    ...            <hosts>
    ...                <host name="shell1.adytum.us">
    ...                    <escalation enabled="false">
    ...                        <group level="0">
    ...                            <maillist>
    ...                                <email>oubiwann@myrealbox.com</email>
    ...                                <email>oubiwann@yahoo.com</email>
    ...                            </maillist>
    ...                        </group>
    ...                        <group level="1">
    ...                            <maillist></maillist>
    ...                        </group>
    ...                    </escalation>
    ...                    <scheduled_downtime></scheduled_downtime>
    ...                </host>
    ...                <host name="shell2.adytum.us">
    ...                    <escalation enabled="true">
    ...                        <group level="0">
    ...                            <maillist>
    ...                                <email>oubiwann@myrealbox.com</email>
    ...                                <email>oubiwann@yahoo.com</email>
    ...                            </maillist>
    ...                        </group>
    ...                        <group level="1">
    ...                            <maillist></maillist>
    ...                        </group>
    ...                    </escalation>
    ...                    <scheduled_downtime></scheduled_downtime>
    ...                </host>
    ...            </hosts>
    ...        </service>
    ...        <service type="http">
    ...            <defaults/>
    ...            <hosts>
    ...                <host/>
    ...            </hosts>
    ...        </service>
    ...        <service type="dummy">
    ...        </service>
    ...    </services>
    ...    <system>
    ...        <database type="zodb">
    ...            <directory>data/zodb</directory>
    ...            <host>localhost</host>
    ...            <port></port>
    ...            <user></user>
    ...            <password></password>
    ...        </database>
    ...    </system>
    ...    <constants>
    ...    </constants>
    ... </config>"""
    >>> cfg = XmlConfig(xmlstring06)
    >>> cfg.services.service
    >>> for service in cfg.services.service:
    ...   assert(isinstance(service, DictConfig))
    ...   if service.type == 'ping':
    ...     print service.defaults.ping_count
    ...     for host in service.hosts.host:
    ...       print host.name
    ...       print host.escalation.enabled
    ...       for group in host.escalation.group:
    ...           print group.level
    4
    shell1.adytum.us
    false
    0
    1
    shell2.adytum.us
    true
    0
    1
    >>> cfg.system.database.type
    'zodb'
    >>> cfg.system.database.directory
    'data/zodb'
    >>> cfg.system.database.host
    'localhost'
    >>> cfg.system.database.port
    None
    '''
    def __init__(self, xml_source, keep_namespace=True):
        # check if it's a file
        if os.path.isfile(xml_source):
            tree = ElementTree.parse(xml_source)
            root = tree.getroot()
        # check to see if it's a file object
        elif isinstance(xml_source, file):
            root = ElementTree.XML(xml_source.read())
        # if those don't work, treat it as an XML string
        else:
            root = ElementTree.XML(xml_source)
        self._root = root
        xmldict = XmlDictConfig(root, keep_namespace=keep_namespace)
        self._namespace = xmldict._namespace
        self.processDict(xmldict)        
        
def _test():
    import doctest, xml
    return doctest.testmod(xml)

if __name__ == '__main__':
    _test()
