import gtk, os, sys
from xmlrpclib import ServerProxy
from shutil import copyfile
import logging
import paths, util
from prefs import Prefs

class Backend(util.Singleton):
    def __init__(self):
        # First we initialize some buffer and other important variables
        self.downloadingbuffer = []
        self.queuebuffer = []
        self.processingbuffer = []
        self.statusbuffer = {}
        self.downloadlist = []
        self.queuelist = []
        self.processinglist = []
        self.finishedlist = []
        
        self.speed = "0"
        self.running = 0
        self.paused = False
        
        # Then we initialized the download/queue/processing list
        self.list = gtk.ListStore(int, str, str, str, str, int)
        
        # Starting the HellaNZB daemon if we are not in frontend mode
        if not Prefs.lotta["frontend_mode"]:
            self.startHella()
        
        # Now we can connect to the HellaNZB daemon
        self.connect()
    
    def startHella(self):
        try:
            started = 0
            processlist = os.popen2("ps x")
            for process in processlist[1].readlines():
                if "hellanzb" in process:
                    started = 0
                    #logging.info(_("HellaNZB seems to be already running, I'm not starting the daemon."))
                         
            if not started:
                self.hellaProcess = os.popen4(Prefs.lotta["start_command"] + " -c " + paths.clientDir("hellanzb.conf"))
                for line in self.hellaProcess[1].readlines():
                    line = line.strip()
                    if not line == "":
                        logging.info(_("HellaNZB output: " + line))
        except:
            logging.error(_("Could not start the HellaNZB daemon."))
        else:
            logging.info(_("Started HellaNZB daemon."))
    
    def stopHella(self):
        try:
            if not Prefs.lotta["frontend_mode"]:
                self.hellaStopProcess = os.popen4(Prefs.lotta["stop_command"] + " -c " + paths.clientDir("hellanzb.conf"))
                for line in self.hellaStopProcess[1].readlines():
                    line = line.strip()
                    if not line == "":
                        logging.info(_("HellaNZB output: " + line))
                logging.info(_("HellaNZB daemon stopped."))
        except:
            logging.error(_("Could not stop the HellaNZB daemon."))
        else:
            logging.info(_("Bye!"))
    
    def restartHella(self):
        try:
            self.stopHella()
            self.startHella()
        except:
            logging.error(_("Could not restart the HellaNZB daemon."))
        else:
            logging.info(_("Restarted the HellaNZB daemon."))
    
    def connect(self):
        username = "hellanzb"
        
        if not Prefs.lotta["frontend_mode"]:
            password = Prefs.hella["XMLRPC_PASSWORD"]
            address = Prefs.hella["XMLRPC_SERVER"]
            port = str(Prefs.hella["XMLRPC_PORT"])
        else:
            password = Prefs.lotta["xmlrpc_password"]
            address = Prefs.lotta["xmlrpc_address"]
            port = Prefs.lotta["xmlrpc_port"]
        
        try:
            self.server = ServerProxy("http://" + username + ":" + password + "@" + address + ":" + port + "/")
            self.getStatus()
            self.running = 1
        except:
            logging.error(_("Could not connect to the HellaNZB daemon."))
        else:
            logging.info(_("Connected to the HellaNZB daemon."))
    
    def addFile(self, name):
        try:
            self.server.enqueue(name)
            os.remove(name)
        except:
            pass
            # logging.error(_("Could not add file to the download queue."))
        else:
            logging.info(_("Added %s to the download queue.") % (name))
    
    def delFile(self, id):
        if id:
            currentID = self.list.get_value(id, 0)
            
            if currentID == self.downloading[0]["id"]:
                self.server.cancel()
            else:
                self.server.dequeue(currentID)
            
            logging.info(_("Removed %s from queue.") % (currentID))
    
    def moveUp(self, id):
        try:
            if id:
                currentID = self.list.get_value(id, 0)
                
                if self.queue[0]['id'] == currentID:
                    self.server.force(currentID)
                    logging.info("Forced " + currentID + " to begin.")
                else:
                    self.server.up(currentID)
                    logging.info("Moved " + currentID + " up.")
        except:
            logging.error(_("Could not move items."))
    
    def moveDown(self, id):
        try:
            if id:
                if self.list.get_value(id, 0) == self.downloading[0]["id"]:
                    if self.queue != []:
                        currentID = self.list.get_value(self.list.get_iter(1), 0)
                        self.server.force(currentID)
                        logging.info("Forced " + currentID + " to begin.")
                else:
                    currentID = self.list.get_value(id, 0)
                    self.server.down(currentID)
                    logging.info("Moved " + currentID + " down.")
        except:
            logging.error(_("Could not move items."))
    
    def getStatus(self):
        try:
            return self.server.status()
        except:
            self.running = 2
            logging.warning(_("Could not get an update from the HellaNZB daemon, is it (still) running?"))
    
    def updateStatus(self):
        self.status = self.getStatus()
        
        if not self.status:
            logging.warning(_("It seems that HellaNZB isn't running. Shutting down LottaNZB."))
            self.running = 2
        
        elif not self.statusbuffer == self.status:
            if self.status["is_paused"]:
                self.paused = True
                self.updateProgress()
            else:
                self.paused = False
            
            if self.status["currently_downloading"]:
                try:
                    if not self.status["percent_complete"] == self.statusbuffer["percent_complete"]:
                        self.updateProgress()
                except KeyError:
                    pass
            
            self.speed = str(self.status["rate"])
            self.eta = self.getETA(self.status["eta"])
            self.remaining = str(self.status["queued_mb"])
            
            self.downloading = self.status["currently_downloading"]
            self.queue = self.status["queued"]
            self.processing = self.status["currently_processing"]
            
            if not self.processing == self.processingbuffer:
                self.updateProcessing()
                self.processingbuffer = self.processing
            
            if not self.downloading == self.downloadingbuffer:
                self.updateDownloading()
                self.downloadingbuffer = self.downloading
            
            if not self.queue == self.queuebuffer:
                self.updateQueue()
                self.queuebuffer = self.queue
            
            self.statusbuffer = self.status
    
    def updateDownloading(self):
        self.downloadlist = []
        
        for download in self.downloading:
            if len(download["nzbName"].split("--")) > 1:
                category = download["nzbName"].split("--")[0].strip()
                name = download["nzbName"].split("--")[1].strip()
            else:
                category = "Unknown"
                name = download["nzbName"]
            
            size = _("%s MB") % (str(download["total_mb"]))
            
            percentage = min(100, self.status["percent_complete"])
            progress = str(percentage) + "%"
            
            if self.paused:
                progress = _("Paused at: %s") % (progress)
            elif download["is_par_recovery"]:
                progress = _("Downloading PAR recovery files: %s") % (progress)
            
            self.downloadlist.append([download["id"], name, category, size, progress, percentage])
        
        self.updateList()
    
    def updateQueue(self):
        self.queuelist = []
        
        for item in self.queue:
            if len(item["nzbName"].split("--")) > 1:
                category = item["nzbName"].split("--")[0].strip()
                name = item["nzbName"].split("--")[1].strip()
            else:
                category = _("Unknown")
                name = item["nzbName"]
            percentage = 0
            if item["is_par_recovery"]:
                progress = _("Queued: Need PAR recovery")
            else:
                progress = _("Queued")
            try:
                size = _("%s MB") % (str(item["total_mb"]))
            except:
                size = ""
            
            self.queuelist.append([item["id"], name, category, size, progress, percentage])
        
        self.updateList()
    
    def updateProcessing(self):
        self.processinglist = []
        
        for process in self.processing:
            if len(process["nzbName"].split("--")) > 1:
                category = process["nzbName"].split("--")[0].strip()
                name = process["nzbName"].split("--")[1].strip()
            else:
                category = _("Unknown")
                name = process["nzbName"]
            
            percentage = 100
            
            if process["is_par_recovery"]:
                progress = _("Repairing and extracting")
            else:
                progress = _("Processing")
            
            size = ""
            self.processinglist.append([process["id"], name, category, size, progress, percentage])
        
        templist = []
        
        for buffered in self.processingbuffer:
            if buffered not in self.processing:
                found = 0
                for download in self.downloading:
                    if download["id"] == buffered["id"]:
                        found = 1          
                if not found:
                    templist.append(buffered)
        
        for finished in templist:
            if len(finished["nzbName"].split("--")) > 1:
                category = finished["nzbName"].split("--")[0].strip()
                name = finished["nzbName"].split("--")[1].strip()
            else:
                category = _("Unknown")
                name = finished["nzbName"]
            
            percentage = 100
            
            progress = _("Finished")
            size = ""
            self.finishedlist.append([finished["id"], name, category, size, progress, percentage])
        
        self.updateList()
    
    def clearFinished(self):
        if not self.finishedlist == []: 
            self.finishedlist = []
            self.updateList()
            logging.info(_("Cleared the finished items."))
    
    def updateProgress(self):
        if not self.downloading == []:
            iter = self.list.get_iter_first()
            
            if iter:
                percentage = min(100, self.status["percent_complete"])
                
                if self.paused:
                    progress = _("Paused at: %s%%") % (str(percentage))
                else:
                    progress = str(percentage) + "%"
                
                self.list.set(iter, 4, progress)
                self.list.set(iter, 5, percentage)
    
    def updateList(self):
        self.list.clear()
        
        for item in self.downloadlist:
            self.list.append(item)
        
        for item in self.queuelist:
            self.list.append(item)
         
        for item in self.processinglist:
            self.list.append(item)
        
        for item in self.finishedlist:
            self.list.append(item)
    
    def pause(self):
        try:
            self.paused = True
            self.server.pause()
        except:
            logging.error(_("Could not pause the download."))
        else:
            logging.info(_("Paused downloads."))
    
    def resume(self):
        try:
            self.paused = False
            self.hellaResumeProcess = os.popen4(Prefs.lotta["resume_command"])
        except:
            logging.error(_("Could not resume the download."))
        else:
            logging.info(_("Resuming downloads."))
    
    def getETA(self, etaSeconds):
        hours = int(etaSeconds / (60 * 60))
        minutes = int((etaSeconds - (hours * 60 * 60)) / 60)
        seconds = etaSeconds - (hours * 60 * 60) - (minutes * 60)
        
        return "%.2d:%.2d:%.2d" % (hours, minutes, seconds)
    
    def quit(self):
        self.running = 0
        self.stopHella()
        sys.exit(1)
    
    def leave(self):
        sys.exit()
