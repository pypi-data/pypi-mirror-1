import gtk, os, logging
import util
from prefs import Prefs
import logging

class FrontModeDialog:
    def __init__(self):
        self.uiTree = util.UITree("PreferencesFront")
        self.window = self.uiTree.get_root_widget()
        
        self.uiTree.signal_autoconnect({
            "on_PreferencesFrontButtonCancel_clicked" : self.hide,
            "on_PreferencesFrontButtonSave_clicked" : self.save
        })
        
        self.fields = self.uiTree.get_widget_dict(["Address", "Port", "Password"])
        
        self.fill()
        self.window.show()
    
    def fill(self):
        for field, widget in self.fields.iteritems():
            widget.set_text(Prefs.lotta["xmlrpc_" + field])
    
    def hide(self, *args):
        self.window.hide()
    
    def save(self, *args):
        for field, widget in self.fields.iteritems():
            Prefs.lotta["xmlrpc_" + field] = widget.get_text()
        
        Prefs.lotta.save()
        
        self.hide()

class StandaloneModeDialog:
    def __init__(self):
        # Here we initialize the server list
        self.serverList = gtk.ListStore(str, str, str)
        
        self.uiTree = util.UITree("Preferences")
        self.window = self.uiTree.get_root_widget()
        
        self.uiTree.signal_autoconnect({
            "on_PreferencesButtonCancel_clicked" : self.hide,
            "on_PreferencesButtonSave_clicked" : self.save,
            "on_PreferencesServerEditButton_clicked" : self.editServer,
            "on_PreferencesServerAddButton_clicked" : self.addServer,
            "on_PreferencesServerDeleteButton_clicked" : self.removeServer
        })
        
        self.generalFields = self.uiTree.get_widget_dict(["DownloadDir", "MaxRate", "SmartPar", "Notify", "Minimized"], "PreferencesGeneral")
        self.newzbinFields = self.uiTree.get_widget_dict(["Enabled", "Username", "Password"], "PreferencesNewzbin")
        
        self.serverTreeView = self.uiTree.get_widget("PreferencesServerTreeView")
        self.serverTreeView.set_model(self.serverList)
        self.serverTreeView.set_rules_hint(True)
        self.serverTreeView.show()
        
        for id, title in enumerate([_("Name"), _("Address"), _("Username")]):
            column = gtk.TreeViewColumn(title, gtk.CellRendererText(), text=id)
            column.set_resizable(True)
            column.set_expand(True)
            self.serverTreeView.append_column(column)
        
        self.fill()
        self.window.run()
    
    def hide(self, *args):
        self.window.hide()
    
    def fill(self):
        self.generalFields["downloaddir"].set_current_folder(Prefs.hella["DEST_DIR"])
        
        if "MAX_RATE" in Prefs.hella:
            self.generalFields["maxrate"].set_text(str(Prefs.hella["MAX_RATE"]))
        
        checkboxes = {
            "smartpar"  : Prefs.hella["SMART_PAR"],
            "notify"    : Prefs.hella["LIBNOTIFY_NOTIFY"],
            "minimized" : Prefs.lotta["start_minimized"]
        }
        
        for field, preference in checkboxes.iteritems():
            self.generalFields[field].set_active((True if preference else False))
        
        # Now we fill in the values on the Newzbin.com tab
        # Fill in the enable checkbox and the username and password
        newzbinEnabled = (True if Prefs.hella["NEWZBIN_USERNAME"] and Prefs.hella["NEWZBIN_PASSWORD"] else False)
        
        self.newzbinFields["enabled"].set_active(newzbinEnabled)
        self.newzbinFields["username"].set_text((Prefs.hella["NEWZBIN_USERNAME"] if newzbinEnabled else ""))
        self.newzbinFields["password"].set_text((Prefs.hella["NEWZBIN_PASSWORD"] if newzbinEnabled else ""))
        
        self.fillServerList()
    
    def fillServerList(self):
        self.serverList.clear()
        
        for server in Prefs.hella.servers:
            self.serverList.append([server.id, server.getDefaultHost().address, server.username])
    
    def save(self, *args):
        try:
            Prefs.hella["MAX_RATE"] = int(self.generalFields["maxrate"].get_text())
        except:
            pass
        
        Prefs.hella.setFromDict({
            "DEST_DIR" : self.generalFields["downloaddir"].get_current_folder(),
            "SMART_PAR" : self.generalFields["smartpar"].get_active(),
            "LIBNOTIFY_NOTIFY" : self.generalFields["notify"].get_active(),
            "NEWZBIN_USERNAME" : self.newzbinFields["username"].get_text(),
            "NEWZBIN_PASSWORD" : self.newzbinFields["password"].get_text()
        })
        
        Prefs.hella.save()
        
        Prefs.lotta["start_minimized"] = self.generalFields["minimized"].get_active()
        Prefs.lotta.save()
        
        self.hide()
    
    def getSelectedServer(self):
        selection = self.serverTreeView.get_selection()
        model, selection_iter = selection.get_selected()
        
        if selection_iter:
            server = self.serverList.get_value(selection_iter, 0)
            
            return Prefs.hella.getServerByName(server)
        else:
            return None
    
    def editServer(self, *args):
        server = self.getSelectedServer()
        
        if server:
            dialog = EditServerDialog(server)
            self.fillServerList()
    
    def addServer(self, *args):
        dialog = AddServerDialog()
        self.fillServerList()
    
    def removeServer(self, *args):
        server = self.getSelectedServer()
        
        if server:
            dialog = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, buttons=gtk.BUTTONS_OK_CANCEL, \
                type=gtk.MESSAGE_QUESTION, message_format=_("Are you sure you want to delete this server?"))
            
            response = dialog.run()
            dialog.destroy()
            
            if response == gtk.RESPONSE_OK:
                try:
                    Prefs.hella.servers.remove(server)
                    Prefs.hella.save()
                    
                    self.fillServerList()
                except:
                    logging.error(_("Could not delete server."))

class AbstractServerDialog:
    def __init__(self):
        self.uiTree = util.UITree("ServerDialog")
        self.window = self.uiTree.get_root_widget()
        
        self.fields = self.uiTree.get_widget_dict(["Name", "Address", "Port", "Username", "Password", "SSL", "Connections"])
        
        self.uiTree.signal_autoconnect({
            "on_ServerDialogApplyButton_clicked" : self.saveHandler,
            "on_ServerDialogCancelButton_clicked" : self.close
        })
    
    def getInput(self, *args):
        input = {
            "id" : self.fields["name"].get_text(),
            "hosts" : [self.fields["address"].get_text() + ":" + self.fields["port"].get_text()],
            "username" : self.fields["username"].get_text(),
            "password" : self.fields["password"].get_text(),
            "ssl" : self.fields["ssl"].get_active(),
            "connections" : self.fields["connections"].get_value()
        }
        
        return input
    
    def close(self, *args):
        self.window.destroy()
    
    def saveHandler(self, *args):
        self.save()
    
    def save(self):
        pass

class EditServerDialog(AbstractServerDialog):
    def __init__(self, server):
        AbstractServerDialog.__init__(self)
        
        self.server = server
        self.fill()
        
        self.window.set_title(_("Edit server")) 
        self.window.run()
    
    def fill(self):
        host = self.server.getDefaultHost()
        
        self.fields["name"].set_text(self.server.id)
        self.fields["address"].set_text(host.address)
        self.fields["port"].set_text(host.port)
        self.fields["username"].set_text(self.server.username)
        self.fields["password"].set_text(self.server.password)
        self.fields["ssl"].set_active(self.server.ssl)
        self.fields["connections"].set_value(self.server.connections)
    
    def save(self):
        self.server.setFromDict(self.getInput())
        Prefs.hella.save()
        self.close()
        
class AddServerDialog(AbstractServerDialog):
    def __init__(self):
        AbstractServerDialog.__init__(self)
        
        self.window.set_title(_("Add a new server"))
        self.window.run()
    
    def save(self):
        Prefs.hella.addServer(self.getInput())
        Prefs.hella.save()
        self.close()
