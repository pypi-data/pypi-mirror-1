import gtk, gtk.glade
import os, logging
import paths, util
from prefs import Prefs, HellaPrefs

class Assistant:
    def __init__(self, firstRun):
        if firstRun:
            try:
                paths.makeClientDir()
                paths.makeTempDir()
            except:
                logging.error(_("Could not create the LottaNZB directory %s.") % (paths.clientDir()))
            else:
                logging.info(_("Created the LottaNZB directory %s.") % (paths.clientDir()))
        
        self.uiTree = util.UITree("Assistant")
        
        self.assistant = self.uiTree.get_root_widget()
        self.pages = self.uiTree.get_widget_dict(["Intro", "Usage", "Server", "Frontend", "Complete"], "AssistantPage")
        self.modes = self.uiTree.get_widget_dict(["Standalone", "Frontend", "FrontendRemote"], "AssistantUsage")
        self.serverfields = self.uiTree.get_widget_dict(["Username", "Password", "Address", "Port"], "AssistantServer")
        self.frontendfields = self.uiTree.get_widget_dict(["Address", "Port", "Password"], "AssistantFrontend")
        
        self.uiTree.signal_autoconnect({
            "on_Assistant_prepare" : self.handlePageChange,
            "on_Assistant_apply"   : self.finish,
            "on_Assistant_cancel"  : self.close,
        })
        
        self.setMode("standalone")
        
        def handleModeToggle(widget, mode):
            if widget.get_active():
                self.setMode(mode)
        
        for mode, widget in self.modes.iteritems():
            widget.connect("toggled", handleModeToggle, mode)
        
        self.setupPageCheck(self.serverfields, "server")
        self.setupPageCheck(self.frontendfields, "frontend")
        
        self.assistant.set_page_complete(self.pages["intro"], True)
        self.assistant.set_page_complete(self.pages["usage"], True)
        self.assistant.set_page_complete(self.pages["complete"], True)
        self.assistant.show()
    
    def handlePageChange(self, page, data):
        newPage = self.assistant.get_current_page() + 1
        
        if newPage == 3:
            confFile = HellaPrefs.locate()
            
            if confFile and Prefs.hella.load(confFile) and Prefs.hella.hasServers():
                server = Prefs.hella.servers[0]
                
                self.serverfields["username"].set_text(server.username)
                self.serverfields["password"].set_text(server.password)
                self.serverfields["address"].set_text(server.getDefaultHost().address)
                self.serverfields["port"].set_text(server.getDefaultHost().port)
        elif newPage == 4:
            if self.mode == "frontend":
                self.frontendfields["address"].set_text("localhost")
            elif self.mode == "frontendremote":
                self.frontendfields["address"].set_text("")
        elif newPage == 5:
            self.setDefaultLottaPrefs()
            
            if self.mode == "standalone":
                serverInfo = {
                    "username" : self.serverfields["username"].get_text(),
                    "password" : self.serverfields["password"].get_text(),
                    "hosts"    : [self.serverfields["address"].get_text() + ":" + self.serverfields["port"].get_text()],
                }
                
                if Prefs.hella.hasServers():
                    Prefs.hella.servers[0].setFromDict(serverInfo)
                else:
                    serverInfo["id"] = "LottaNZB"
                    Prefs.hella.addServer(serverInfo)
                
                if not Prefs.hella.loaded:
                    self.setDefaultHellaPrefs()
                
                try:
                    Prefs.hella.save(paths.clientDir("hellanzb.conf"))
                except:
                    logging.error(_("Could not write the hellanzb.conf file."))
                else:
                    logging.info(_("Wrote the hellanzb.conf file."))
            elif self.mode == "frontend" or self.mode == "frontendremote":
                Prefs.lotta.setFromDict({
                    "frontend_mode"         : True,
                    "remote"                : self.mode == "frontendremote"
                })
            
                if Prefs.lotta.loaded:
                    Prefs.lotta.setFromDict({
                        "xmlrpc_address"    : Prefs.hella["XMLRPC_SERVER"],
                        "xmlrpc_port"       : Prefs.hella["XMLRPC_PORT"],
                        "xmlrpc_password"   : Prefs.hella["XMLRPC_PASSWORD"]
                    })
                else:
                    Prefs.lotta.setFromDict({
                        "xmlrpc_address"    : self.frontendfields["address"].get_text(),
                        "xmlrpc_port"       : self.frontendfields["port"].get_text(),
                        "xmlrpc_password"   : self.frontendfields["password"].get_text()
                    })
            
            Prefs.lotta.save()
    
    def setMode(self, mode):
        for page in ["server", "frontend"]:
            self.pages[page].hide()
        
        if mode == "standalone":
            self.pages["server"].show()
        elif mode == "frontend":
            confFile = HellaPrefs.locate()
            
            if not (confFile and Prefs.hella.load(confFile)):
                self.pages["frontend"].show()
        elif mode == "frontendremote":
            self.pages["frontend"].show()
        
        self.mode = mode
        self.assistant.update_buttons_state()
    
    def setupPageCheck(self, fields, page):
        def handleInput(*args):
            inputOK = True
            
            for field, widget in fields.iteritems():
                if len(widget.get_text()) <= 0:
                    inputOK = False
            
            self.assistant.set_page_complete(self.pages[page], inputOK)
        
        for field, widget in fields.iteritems():
            widget.connect("changed", handleInput)
    
    def setDefaultHellaPrefs(self):
        cDir = paths.clientDir
        
        Prefs.hella.setFromDict({
            "PREFIX_DIR"                : cDir(),
            "QUEUE_DIR"                 : cDir("nzb/daemon.queue/"),
            "CURRENT_DIR"               : cDir("nzb/daemon.current/"),
            "PROCESSING_DIR"            : cDir("nzb/daemon.processing/"),
            "WORKING_DIR"               : cDir("nzb/daemon.working/"),
            "TEMP_DIR"                  : cDir("nzb/daemon.temp/"),
            "STATE_XML_FILE"            : cDir("nzb/hellanzbState.xml"),
            "POSTPONED_DIR"             : cDir("nzb/daemon.postponed/"),
            "DEST_DIR"                  : paths.homeDir("Desktop"),
            "XMLRPC_SERVER_BIND"        : "127.0.0.1",
            "PROCESSED_SUBDIR"          : "processed",
            "LOG_FILE"                  : "/var/tmp/hellanzb.log",
            "LOG_FILE_BACKUP_COUNT"     : 0,
            "LOG_FILE_MAX_BYTES"        : 0,
            "KEEP_FILE_TYPES"           : ["nfo", "txt"],
            "NOT_REQUIRED_FILE_TYPES"   : ["log", "m3u", "nfo", "nzb", "sfv", "txt"],
            "GROWL_PASSWORD"            : "password",
            "CATEGORIZE_DEST"           : True,
            "SMART_PAR"                 : True,
            "MAX_DECOMPRESSION_THREADS" : 2,
            "DELETE_PROCESSED"          : True,
            "GROWL_NOTIFY"              : False,
            "GROWL_SERVER"              : "IP",
            "LIBNOTIFY_NOTIFY"          : False,
            "XMLRPC_SERVER"             : "localhost",
            "XMLRPC_PORT"               : 8760,
            "XMLRPC_PASSWORD"           : "changeme",
            "NEWZBIN_USERNAME"          : None,
            "NEWZBIN_PASSWORD"          : None
        })
    
    def setDefaultLottaPrefs(self):
        cmd = self.getHellaCommand()
        
        Prefs.lotta.setFromDict({
            "frontend_mode"             : False,
            "remote"                    : False,
            "sleep_time"                : 1.0,
            "window_height"             : 350,
            "window_width"              : 700,
            "start_minimized"           : False,
            "resume_command"            : cmd + " continue",
            "start_command"             : cmd + " -D",
            "stop_command"              : cmd + " shutdown",
            "xmlrpc_address"            : "localhost",
            "xmlrpc_port"               : 8760,
            "xmlrpc_password"           : "changeme"
        })
    
    def getHellaCommand(self):
        places = ["/usr/bin/hellanzb", "/usr/bin/hellanzb.py", "/usr/local/bin/hellanzb", "/usr/local/bin/hellanzb.py"]
        
        for place in places:
            if os.path.isfile(place):
                return place
    
    def finish(self, *args):
        logging.info(_("The preferences were correctly written."))
        self.close()
    
    def close(self, *args):
        logging.info(_("Closed the configuration assistant."))
        gtk.main_quit()
