############################################################################
#    Copyright (C) 2004 by Lethalman                                       #
#    lethalman@fyrebird.net                                                #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

import sys, re
from xml.dom.minidom import parse
from string import strip

__doc__ = """
This util helps pyIS to check and organize the config file
@author: Lethalman
@var config: Configuration file
@type config: Module
@var lowdict: Quick reference to the utils.general.lowdict function
@type lowdict: Function
@var lowlist: Quick reference to the utils.general.lowlist function
@type lowlist: Function
"""

lowdict=None
lowlist=None

class Element:
    def __init__(self, node):
        """
        Make an hierarchy of the XML node
        """
        self.node = node
        self.name = self.node.nodeName
        self.value = ""
        self.data = {}
        for node in self.node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                self.value += node.nodeValue
            elif node.nodeType == node.ELEMENT_NODE:
                if not node.nodeName in self.data: self.data[node.nodeName] = []
                self.data[node.nodeName].append(Element(node))
        self.attrs = {}
        if not self.node.attributes: return
        for nattr in range(self.node.attributes.length):
            attr = self.node.attributes.item(nattr)
            self.attrs[attr.name] = attr.value
        
    def __getitem__(self, item):
        """
        Return a child of this XML element
        """
        return self.data[item]
        
    def __setitem__(self, item, value):
        """
        Overwrite a value
        """
        self.data[item] = value
        
    __str__ = __repr__ = lambda self: str(self.value)
        
def getConfig():
    raw = parse("config.xml")
    for config in raw.childNodes:
        if config.nodeType == config.ELEMENT_NODE: break
    if config.nodeName != 'config':
        return "configuration file needs 'config' tag as its root document node"
    config = Element(config)
    
    def default(element, attr, value, func=str):
        """
        Set a default attribute for an element. If it already exists
        convert it by using the given function.
        @param element: Element
        @param attr: Attribute name
        @param value: Default value
        @param func: converter function
        """
        if 'port' in element.attrs: element.attrs[attr] = func(element.attrs[attr])
        else: element.attrs[attr] = value
        
    def convert(element, func=int):
        """
        Convert an element value using the given functions.
        @param element: Element
        @param func: converter function
        """
        element.value = func(element.value)
    
    def unique(dict, key):
        """
        Replace a list contained into a dict value with its
        first element. If the list contains more than one
        elements, raise an exception.
        """
        assert len(dict[key]) == 1, "there should be one %r tag" % key
        dict[key] = dict[key][0]
        return dict[key]
    
    # Server section
    try: unique(config, 'server')
    except: return "missed server configuration!"
    server = config['server']
    default(server, 'type', "hub")
    try:
        for i in server['listen']:
            default(i, 'port', 6667, int)
        for i in ('name', 'netname'): unique(server, i)
        convert(unique(server, 'maxconnections'))
        default(unique(server, 'password'), 'crypt', 'no')
    except:
        return "server section: "+str(sys.exc_value)
        
    # Module section(s)
    if 'modules' in config.data:
        for i in config['modules']: convert(i, strip)
    
    # Admin section
    try: unique(config, 'admin')
    except: return "missed admin configuration!"
    
    # Client section
    try: unique(config, 'client')
    except: return "missed client configuration!"
    client = config['client']
    try:
        convert(unique(client, 'timeout'))
        unique(client, 'badformats')
        hierarchy = unique(client, 'hierarchy')
        assert 'value' in hierarchy.attrs, "'value' attribute in hierarchy not found"
        convert(unique(hierarchy, 'allmodes'), strip)
        for i in hierarchy['mode']:
            assert 'name' in i.attrs, "'mode' attribute in hierarchy mode not found"
            if 'modes' in i.data: convert(unique(i, 'modes'), strip)
            if 'commands' in i.data: unique(i, 'commands')
        if 'modes' in hierarchy.data: convert(unique(hierarchy, 'modes'), strip)
        unique(client, 'perform')
        convert(unique(client, 'maxoptions'))
        unique(client, 'idle')
        convert(unique(client, 'maxlength'))
        for i in client['badwords']:
            assert 'replace' in i.attrs, "'replace' attribute in badwords not found"
        convert(unique(client, 'virtualhost'), strip)
    except:
        return "client section: "+str(sys.exc_value)
        
    # Channel section
    try: unique(config, 'channel')
    except: return "missed channel configuration!"
    channel = config['channel']
    try:
        unique(channel, 'badformats')
        hierarchy = unique(channel, 'hierarchy')
        assert 'value' in hierarchy.attrs, "'value' attribute in hierarchy not found"
        convert(unique(hierarchy, 'allmodes'), strip)
        for i in hierarchy['mode']:
            assert 'name' in i.attrs, "'mode' attribute in hierarchy mode not found"
            if 'modes' in i.data: convert(unique(i, 'modes'), strip)
            if 'commands' in i.data: unique(i, 'commands')
            if 'command' in i.data:
                for ii in i['command']:
                    assert 'mode' in ii.attrs, "'mode' attribute in hierarchy mode command not found"
        if 'modes' in hierarchy.data: convert(unique(hierarchy, 'modes'), strip)
        convert(unique(channel, 'requirearg'), strip)
        unique(channel, 'perform')
        convert(unique(channel, 'maxlength'))
        for i in client['badwords']:
            assert 'replace' in i.attrs, "'replace' attribute in badwords not found"
    except:
        return "channel section: "+str(sys.exc_value)
        
    # Oper section(s)
    if 'oper' in config.data:
        try:
            for i in config['oper']:
                assert 'user' in i.attrs, "'user' attribute in oper not found"
                default(i, 'name', 'IRCop')
                unique(i, 'userhost')
                convert(unique(client, 'virtualhost'), strip)
        except:
            return "oper section: "+str(sys.exc_value)
        
    # Link section(s)
    if 'link' in config.data:
        try:
            for i in config['link']:
                assert 'name' in i.attrs, "'name' attribute in link not found"
                default(unique(server, 'password'), 'crypt', 'no')
                convert(unique(i, 'protocol'), strip)
        except:
            return "link section: "+str(sys.exc_value)
            
    # Log section
    try: unique(config, 'log')
    except: return "missed log configuration!"
    log = config['log']
    try:
        assert 'file' in log.attrs, "'file' attribute in log not found"
        unique(log, 'format')
        unique(log, 'internals')
        unique(log, 'commands')
    except:
        return "log section: "+str(sys.exc_value)
        
    # Alias section(s)
    if 'alias' in config.data:
        try:
            for i in config['alias']:
                assert 'cmd' in i.attrs, "'cmd' attribute in alias not found"
        except:
            return "alias section: "+str(sys.exc_value)
    
    # Class section(s)
    try:
        for i in config['class']:
            assert 'name' in i.attrs, "'name' attribute in class not found"
            convert(i, strip)
    except:
        return "class section: "+str(sys.exc_value)
        
    # Util section(s)
    try:
        for i in config['util']:
            convert(i, strip)
    except:
        return "util section: "+str(sys.exc_value)
        
    return config
