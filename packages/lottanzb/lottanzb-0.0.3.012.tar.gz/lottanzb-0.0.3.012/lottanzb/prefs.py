import sys, os, logging
from xml.etree.ElementTree import ElementTree, Element, SubElement
import paths

class PrefsBase(dict):
    def setFromDict(self, prefDict):
        for key, value in prefDict.iteritems():
            self[key] = value
    
    def setConfigFile(self, confFile):
        self.confFile = confFile
        
    def __getitem__(self, key):
        if key in self:
            return dict.__getitem__(self, key)
        else:
            return None

class HellaPrefs(PrefsBase):
    def __init__(self):
        self.servers = []
        self.loaded = False
        self.confFile = paths.clientDir("hellanzb.conf")
    
    def load(self, confFile=None):
        if not confFile is None:
            self.setConfigFile(confFile)
        
        if os.path.isfile(self.confFile):
            self.loaded = False
            
            # Clear the preferences and server list before importing the config file
            self.clear()
            
            def defineServer(**args):
                self.addServer(args)
            
            def defineMusicType(*args):
                pass
            
            Hellanzb = ConfigStub()
            execfile(self.confFile)
            
            def fillInPrefs(propertyList):
                for property in propertyList:
                    if hasattr(Hellanzb, property):
                        self[property] = getattr(Hellanzb, property)
            
            fillInPrefs(HellaPrefs.STRING_PREFS)
            fillInPrefs(HellaPrefs.BOOL_NUM_PREFS)
            fillInPrefs(HellaPrefs.LIST_PREFS)
            
            self.loaded = True
            return True
        else:
            return False
    
    def clear(self):
        dict.clear(self)
        self.servers[:] = []
    
    def addServer(self, args):
        self.servers.append(Server(args))
    
    def hasServers(self):
        return len(self.servers) > 0
    
    def getServerByName(self, name):
        for server in self.servers:
            if server.id == name:
                return server
        
        return None
    
    def save(self, confFile=None):
        if not confFile is None:
            self.setConfigFile(confFile)
        
        output = ""
        
        def toOutput(propertyList, **args):
            retval = ""
            
            for property in propertyList:
                if property in self:
                    value = self[property]
                    
                    if "transform" in args:
                        value = args["transform"](value)
                    
                    if "glue" in args:
                        value = args["glue"] + value + args["glue"]
                else:
                    value = str(False)
                    retval += "# "
                
                retval += "Hellanzb." + property + " = " + value + "\n"
            
            return retval
        
        def toList(list):
            listOutput = ""
            
            for item in list:
                listOutput += "\"" + item + "\","
            
            return "[" + listOutput[:-1] + "]"
        
        output += toOutput(HellaPrefs.STRING_PREFS, glue="\"")
        output += toOutput(HellaPrefs.BOOL_NUM_PREFS, transform=str)
        output += toOutput(HellaPrefs.LIST_PREFS, transform=toList)
        
        for server in self.servers:
            output += server.getConfigStr()
        
        confFile = open(self.confFile, "w")
        confFile.write(output)
        confFile.close()
        
    def locate():
        places = [ \
            paths.clientDir(), \
            os.getcwd(), \
            os.path.join(os.getcwd(), "etc"), \
            paths.homeDir(".hellanzb"), \
            os.path.join(sys.prefix, "etc"), \
            "/etc", \
            os.path.join("/etc", "hellanzb") \
        ]
        
        for place in places:
            file = os.path.join(place, "hellanzb.conf")
            
            if os.path.isfile(file):
                return file
    
    locate = staticmethod(locate)
    
    STRING_PREFS   = ["PREFIX_DIR", "GROWL_PASSWORD", "QUEUE_DIR", "XMLRPC_PASSWORD",
                      "CURRENT_DIR", "PROCESSING_DIR", "LOG_FILE", "DEST_DIR",
                      "TEMP_DIR", "GROWL_SERVER", "XMLRPC_SERVER", "STATE_XML_FILE",
                      "PROCESSED_SUBDIR", "POSTPONED_DIR", "MACBINCONV_CMD",
                      "UNRAR_CMD", "PAR2_CMD", "WORKING_DIR", "XMLRPC_SERVER_BIND"]
    
    BOOL_NUM_PREFS = ["DELETE_PROCESSED", "SKIP_UNRAR", "NZBQUEUE_MDELAY",
                      "CATEGORIZE_DEST", "OTHER_NZB_FILE_TYPES", "MAX_DECOMPRESSION_THREADS",
                      "DISABLE_ANSI", "GROWL_NOTIFY", "LOG_FILE_MAX_BYTES",
                      "NZB_ZIPS", "DELETE_PROCESSED", "EXTERNAL_HANDLER_SCRIPT",
                      "CHACHE_LIMIT", "XMLRPC_PORT", "LOG_FILE_BACKUP_COUNT",
                      "LIBNOTIFY_NOTIFY", "UMASK", "SMART_PAR", "NZB_GZIPS",
                      "DISABLE_COLORS", "MAX_RATE", "DEBUG_MODE"]
    
    LIST_PREFS     = ["KEEP_FILE_TYPES", "NOT_REQUIRED_FILE_TYPES"]

class Server:
    def __init__(self, info):
        self.hosts = []
        self.connections = 8
        self.antiIdle = 270
        self.ssl = False
        
        self.setFromDict(info)
    
    def getConfigStr(self):
        hostList = ""
        template = "defineServer(id = \"%s\", username = \"%s\", password = \"%s\", " + \
            "antiIdle = %s, connections = %s, ssl = %s, hosts = [%s])\n"
        
        for host in self.hosts:
            hostList += "\"" + host.getURI() + "\","
        
        return template % (self.id, self.username, self.password, str(self.antiIdle), str(self.connections), str(self.ssl), hostList[:-1])
    
    def setFromDict(self, info):
        for key, var in info.iteritems():
            if not key == "hosts":
                setattr(self, key, var)
        
        if "hosts" in info:
            self.hosts[:] = []
            
            for host in info["hosts"]:
                if isinstance(host, Host):
                    self.hosts.append(host)
                else:
                    self.hosts.append(Host(combined=host))
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        return setattr(self, key, value)
    
    def getDefaultHost(self):
        return self.hosts[0]

class Host:
    def __init__(self, **args):
        if "combined" in args:
            self.setURI(args["combined"])
        elif "address" in args:
            self.address = args["address"]
            
            if "port" in args:
                self.port = args["port"]
            else:
                self.port = 119
    
    def getURI(self):
        return self.address + ":" + self.port
    
    def setURI(self, uri):
        self.address = uri.split(":")[0]
        self.port = uri.split(":")[1]

class LottaPrefs(PrefsBase):
    def __init__(self):
        self.confFile = paths.clientDir("lottanzb.xml")
        self.loaded = False
        
        self.load()
    
    def load(self):
        if os.path.isfile(self.confFile):
            self.loaded = False
            self.clear()
            
            tree = ElementTree(file=self.confFile)
            root = tree.getroot()
            
            for key in list(root):
                type = key.attrib["type"]
                value = key.text
                
                if type == "int":
                    value = int(value)
                elif type == "bool":
                    value = value == "True"
                elif type == "float":
                    value = float(value)
                
                self[key.tag] = value
            
            self.loaded = True
            return True
        else:
            return False
    
    def save(self):
        root = Element("lottaprefs")
        
        for key, value in self.iteritems():
            if isinstance(value, str):
                type = "str"
            elif isinstance(value, bool):
                type = "bool"
            elif isinstance(value, float):
                type = "float"
            elif isinstance(value, int):
                type = "int"
            
            subElement = SubElement(root, key, { "type": type })
            subElement.text = str(self[key])
        
        tree = ElementTree(root)
        tree.write(self.confFile, "utf-8")

class Prefs:
    lotta = LottaPrefs()
    hella = HellaPrefs()

class ConfigStub:
    pass
