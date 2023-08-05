#!/usr/bin/env python
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

import sys, os, signal, exceptions
from xml.dom.minidom import parse
from string import strip
from platform import system
from optparse import OptionParser
from info import version

class Utils: pass

class Common:
    """
    The Common class is used to make an instance containing informations for the whole server
    @ivar addcommand: Add an user command
    @type addcommand: Function
    @ivar saddcommand: Add a server command
    @type saddcommand: Function
    @ivar commands: Dict of commands. Each command can be handled by many functions
    @type commands: Dict
    @ivar modules: List of loaded modules
    @type modules: List
    @ivar utils: Contains pyIS Utilities
    @type utils: Utils instance
    @ivar whowas: History of old nickname data
    @type whowas: Dict
    """
    
    class Element:
        def __init__(self, node):
            """
            Make recursively a pythonic hierarchy of the XML node
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
                    self.data[node.nodeName].append(Common.Element(node))
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
            Overwrite an XML element
            """
            self.data[item] = value
            
        __str__ = __repr__ = lambda self: str(self.value)
        __int__ = lambda self: int(self.value)
        __float__ = lambda self: float(self.value)
    
    def __init__(self, configfile="config.xml"):
        """
        Initialize the instance
        """
        from platform import system
        self.commands = {}
        self.modules = set()
        self.utils = Utils()
        self.whowas = {}
        self.system = system()
        self.configfile = configfile

    def __add(self, cmd, func, pos, d):
        cmd = cmd.lower()
        if not cmd in d: d[cmd] = []
        d[cmd].insert(pos, func)
        
    def addcommand(self, cmd, func, pos=0):
        """
        Add a normal user command
        @param cmd: The command name
        @param func: The function to be called
        @param pos: The position respect the other command handlers of the same command name
        """
        self.__add(cmd, func, pos, self.commands)
        
    def __delitem__(self, item):
        """
        Remove a specified module
        @param item: Module to remove
        """
        for c in [cmd for cmd in self.commands]:
            for f in item.__functions__:
                while f in self.commands[c]: del self.commands[c][self.commands[c].index(f)]
            if not self.commands[c]: del self.commands[c]
        self.modules.remove(item)
        
    def getConfig(self):
        """
        Convert XML data to an handable object.
        It starts from the root element config and
        recurse down to convert/control each tag.
        @return: Configuration of config.xml
        @rtype: XML Element
        """
        raw = parse(self.configfile)
        for config in raw.childNodes:
            if config.nodeType == config.ELEMENT_NODE: break
        if config.nodeName != 'config':
            return "configuration file needs 'config' tag as its root document node"
        config = Common.Element(config)
        
        def default(element, attr, value, func=str):
            """
            Set a default attribute for an element. If it already exists
            convert it by using the given function.
            @param element: Element
            @param attr: Attribute name
            @param value: Default value
            @param func: converter function
            """
            if attr in element.attrs: element.attrs[attr] = func(element.attrs[attr])
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
            @param dict: Element or dict
            @param key: Key to check
            """
            assert len(dict[key]) == 1, "there should be one %r tag" % key
            dict[key] = dict[key][0]
            return dict[key]
            
        def csplit(element, token='\n'):
            """
            Split an element value and strip its content.
            @param element: Element to clear
            """
            element.value = element.value.replace('\t', ' ')
            element.value = filter(lambda x: len(x), [i.strip() for i in (i for i in element.value.split(token))])
            
        def esplit(element, attribute, add=''):
            """
            Split the argument of an element
            char by char. At the end, append
            a further data.
            @param element: Element containing the argument
            @param attribute: The name of the argument
            @param add: Further data to append
            """
            element.attrs[attribute] = map(lambda x:x, element.attrs[attribute])
            if add != None: element.attrs[attribute].append(add)
        
        # Server section
        try: unique(config, 'server')
        except: return sys.exc_value#"missed server configuration!"
        server = config['server']
        default(server, 'type', "hub")
        try:
            for i in server['listen']:
                default(i, 'port', 6667, int)
            for i in ('name', 'netname'): unique(server, i)
            convert(unique(server, 'maxconnections'))
            default(unique(server, 'password'), 'crypt', 'no')
            convert(unique(server, 'motd'), strip)
        except:
            return "server section: "+str(sys.exc_value)
            
        # Module section(s)
        if 'modules' in config.data:
            for i in config['modules']: convert(i, strip)
        
        # Admin section
        try: csplit(unique(config, 'admin'))
        except: return "missed admin configuration!"
        
        # Client section
        try: unique(config, 'client')
        except: return "missed client configuration!"
        client = config['client']
        try:
            convert(unique(client, 'timeout'), float)
            csplit(unique(client, 'badformats'))
            hierarchy = unique(client, 'hierarchy')
            assert 'value' in hierarchy.attrs, "'value' attribute in hierarchy not found"
            esplit(hierarchy, 'value')
            convert(unique(hierarchy, 'allmodes'), strip)
            for i in hierarchy['mode']:
                assert 'name' in i.attrs, "'mode' attribute in hierarchy mode not found"
                if 'modes' in i.data: convert(unique(i, 'modes'), strip)
                if 'commands' in i.data: csplit(unique(i, 'commands'), ' ')
            if 'modes' in hierarchy.data: convert(unique(hierarchy, 'modes'), strip)
            if 'commands' in hierarchy.data: csplit(unique(hierarchy, 'commands'), ' ')
            csplit(unique(client, 'perform'))
            convert(unique(client, 'maxoptions'))
            csplit(unique(client, 'idle'), ' ')
            convert(unique(client, 'maxlength'))
            for i in client['badwords']:
                assert 'replace' in i.attrs, "'replace' attribute in badwords not found"
                csplit(i)
            convert(unique(client, 'virtualhost'), strip)
        except:
            return "client section: "+str(sys.exc_value)
            
        # Channel section
        try: unique(config, 'channel')
        except: return "missed channel configuration!"
        channel = config['channel']
        try:
            csplit(unique(channel, 'badformats'))
            hierarchy = unique(channel, 'hierarchy')
            assert 'value' in hierarchy.attrs, "'value' attribute in hierarchy not found"
            esplit(hierarchy, 'value')
            convert(unique(hierarchy, 'allmodes'), strip)
            for i in hierarchy['mode']:
                assert 'name' in i.attrs, "'mode' attribute in hierarchy mode not found"
                if 'modes' in i.data: convert(unique(i, 'modes'), strip)
                if 'commands' in i.data: csplit(unique(i, 'commands'), ' ')
            if 'modes' in hierarchy.data: convert(unique(hierarchy, 'modes'), strip)
            convert(unique(hierarchy, 'requirearg'), strip)
            csplit(unique(channel, 'perform'))
            convert(unique(channel, 'maxlength'))
            for i in client['badwords']:
                assert 'replace' in i.attrs, "'replace' attribute in badwords not found"
            convert(unique(channel, 'topiclength'))
        except:
            return "channel section: "+str(sys.exc_value)
            
        # Oper section(s)
        if 'oper' in config.data:
            try:
                for i in config['oper']:
                    assert 'user' in i.attrs, "'user' attribute in oper not found"
                    default(i, 'name', 'IRCop')
                    default(unique(i, 'password'), 'crypt', 'no')
                    convert(unique(i, 'modes'), strip)
                    unique(i, 'userhosts')
                    convert(unique(i, 'virtualhost'), strip)
            except:
                return "oper section: "+str(sys.exc_value)
            
        # Link section(s)
        if 'link' in config.data:
            try:
                for i in config['link']:
                    assert 'name' in i.attrs, "'name' attribute in link not found"
                    default(unique(i, 'password'), 'crypt', 'no')
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
            csplit(unique(log, 'internals'), ' ')
            csplit(unique(log, 'commands'), ' ')
        except:
            return "log section: "+str(sys.exc_value)
            
        # Alias section(s)
        if 'alias' in config.data:
            try:
                for i in config['alias']:
                    assert 'cmd' in i.attrs, "'cmd' attribute in alias not found"
                    csplit(i)
            except:
                return "alias section: "+str(sys.exc_value)
        
        # Database section
        if 'database' in config.data:
            db = unique(config, 'database')
            if 'hostname' in db.data:
                unique(db, 'hostname')
                default(db['hostname'], 'port', '5432')
            unique(db, 'dbname')
            unique(db, 'username')
            unique(db, 'password')
            convert(unique(db, 'idle'))
        
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
        
    def DEBUG(self, section, debug):
        """
        Send a debug message to stderr.
        @param section: Code coordinates of this debug
        @param debug: Debug message
        """
        if self.debug: print >> sys.stderr, "\n[DEBUG] %s: %s" % (section, debug)
    
    def excDEBUG(self, section, info):
        """
        Debug an exception traceback. Prints value, type and line number.
        @param section: Code coordinates of this debug
        @param info: Threaded exception informations
        """
        self.DEBUG(section, """
- Error: %s
- Exception Type: %s
- Line Number: %d
        """ % (info[1], str(info[0]).split('.', 1)[1], info[2].tb_lineno))

def main():      
    parser = OptionParser(usage="%prog <start | restart | stop | rehash> [options]", version=version)
    parser.add_option("-c", "--config", dest="config",
            action="store", type = "string", default="config.xml",
            help="specify the XML config file name (default: config.xml)", metavar="FILE")
    parser.add_option("-n", "--nofork", dest="nofork",
            action="store_true", default=False,
            help="do not enter in background mode")
    parser.add_option("-d", "--debug", dest="debug",
            action="store_true", default=False,
            help="show debugging informations on STDOUT")
    (options, args) = parser.parse_args()
    
    if not args:
        parser.print_help()
        sys.exit(-1)
    else: act = args[0]
    def stop():
        try:
            os.kill(int(open("pyis.pid").read()), signal.SIGTERM)
            print "-- pyIrcServer Stopped --"
        except:
            print >> sys.stderr, sys.exc_value
    if act == "rehash":
        try:
            os.kill(int(open("pyis.pid").read()), signal.SIGHUP)
            print "-- pyIrcServer Rehashed --"
        except:
            print >> sys.stderr, sys.exc_value
        sys.exit()
    elif act == "help":
        help()
        sys.exit()
    elif act == "stop":
        stop()
        sys.exit()
    elif act == "restart": 
        stop()
             
    print "-- Starting pyIrcServer --\n"
         
    common = Common(options.config)
    
    if common.system == "Windows": options.nofork = 1
    
    def error(msg=""):
        """
        Send an error message to stderr and exit. If no message is given, then
        get the exception value.
        @param msg: Error message
        """
        if not msg: msg = sys.exc_value
        if sys.exc_type is exceptions.SystemExit: sys.exit(-1)
        print "\nERROR! "+str(msg)
        sys.exit(-1)
        
    def warning(msg=""):
        """
        Send a warning message. If no message is given, then get the
        exception value.
        @param msg: Warning message
        """
        if not msg: msg = sys.exc_value
        print "\nWARNING! "+str(msg)
    
    print "- Checking for %s..." % common.configfile,
    config = common.getConfig()
    if not isinstance(config, common.Element): error(str(config))
    print "\tOK!"
    
    print "- Checking for info.py...",
    try:
        info = __import__("info")
        info.version, info.strictver, info.built, info.website
    except:
        error()
    print "\tOK!"
    
    print "- Checking for classes...",
    try:
        for i in config['class']:
            n = i.attrs['name']
            i = str(i)
            m = getattr(__import__("classes."+i), i)
            setattr(common, n, getattr(m, n))
    except:
        error()
    print "\tOK!"
    
    print "- Checking for utilities...",
    try:
        for i in config['util']:
            i = str(i)
            tu = getattr(__import__("utils."+i), i)
            tu.common = common
            setattr(common.utils, i, tu)
    except:
        error()
    print "\tOK!"
    
    warnings = 0
    print "- Checking for modules...",
    try:
        for m in config['module']:
            m = str(m)
            mod = getattr(__import__("modules."+m), m)
            if mod in common.modules:
                warning("pyIS Module %r already loaded!" % mod)
                warnings = 1
                continue
            try: mod.__functions__
            except:
                warning("pyIS Module %r doesn't seem to have __functions__" % mod)
                warnings = 1
                continue
            mod.__init__(common)
            common.modules.add(mod)
    except:
        error()
    if not warnings: print "\tOK!"
    
    common.config = config
    common.info = info
    common.log = common.Log(common)
    common.debug = options.debug
    
    if config.attrs['backup']:
        open(config.attrs['backup'], "w").write(open("config.xml").read())
    
    if not options.nofork:
        if os.fork(): sys.exit()
    print "* Starting pyIrcServer...",
    svr = common.MainServer(common)
    print "\tOK!"
    svr.read()

if __name__ == '__main__': main()
