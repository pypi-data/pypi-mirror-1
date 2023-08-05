import gtk, os, logging
import gobject
import threading
from time import sleep
from shutil import move
import paths, backend, prefsgui
from prefs import Prefs
import warnings

# Threading should be enabled
gobject.threads_init()

class GUI(threading.Thread):
    def __init__(self):
        # Threading stuffs
        super(GUI, self).__init__()
        
        # Initializing the runner variable, if it is 1 we'll keep on running, if not
        # we quit...
        self.running = 1
        
        #Ignore GtkWarnings
        warnings.simplefilter('ignore', gtk.Warning)
        
        # Now we'll add a notification area icon (statusIcon)
        self.mainStatusIcon = gtk.StatusIcon()
        self.mainStatusIcon.set_from_file(paths.dataDir("icon.png"))
        self.mainStatusIcon.set_tooltip(_("LottaNZB Client"))
        
        self.gtk_screen = self.mainStatusIcon.get_screen()
        colormap = self.gtk_screen.get_rgba_colormap()
        
        if colormap == None:
            colormap = screen.get_rgb_colormap()
        
        gtk.widget_set_default_colormap(colormap)
        
        self.glade = gtk.glade.XML(paths.dataDir("lottanzb.glade"))
        self.mainWindow = self.glade.get_widget("MainWindow")
        
        # Connect to HellaNZB and stuffs
        self.backend = backend.Backend()
        
        if not Prefs.lotta["window_width"]:
            Prefs.lotta["window_width"] = 700
            Prefs.lotta["window_height"] = 300
        
        windowwidth = Prefs.lotta["window_width"]
        windowheight = Prefs.lotta["window_height"]
        
        self.mainWindow.set_default_size(windowwidth, windowheight)
        #self.mainWindow.set_default_size(700, 300)
        
        if Prefs.lotta["start_minimized"]:
            self.mainWindowShow = 0
        else:
            self.mainWindowShow = 1
            self.mainWindow.show()
        
        dic = {
                "on_MainWindow_delete_event" : self.mainWindowHider,
                "on_MainMenuFileAdd_activate" : self.addFile,
                "on_MainMenuFileQuit_activate" : self.destroy,
                "on_MainMenuAbout_activate" : self.about,
                "on_MainToolbarAdd_clicked" : self.addFile,
                "on_MainToolbarRemove_clicked" : self.delFile,
                "on_MainToolbarUp_clicked" : self.moveUp,
                "on_MainToolbarDown_clicked" : self.moveDown,
                "on_MainToolbarPause_toggled" : self.togglePause,
                "on_MainToolbarClear_clicked" : self.clearFinished,
                "on_StatusMenuAdd_activate" : self.addFile,
                "on_StatusMenuQuit_activate" : self.destroy,
                "on_StatusMenuOpen_toggled" : self.mainWindowHider
            }
            
        if Prefs.lotta["frontend_mode"]:
            dic["on_MainMenuEditPreferences_activate"] = self.showFrontmodePreferences
        else:
            dic["on_MainMenuEditPreferences_activate"] = self.showStandalonePreferences
        
        self.glade.signal_autoconnect(dic)
        
        self.mainToolBarPause = self.glade.get_widget("MainToolbarPause")
        
        self.mainSpeedLabel = self.glade.get_widget("MainSpeedLabel")
        self.mainRemainingLabel = self.glade.get_widget("MainRemainingLabel")
        
        self.queueTree = self.glade.get_widget("MainQueueTree")
        self.queueTree.set_model(self.backend.list)
        self.queueTree.enable_model_drag_dest([('text/plain', 0, 0)], gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.queueTree.connect("drag_data_received", self.dragFile)
        
        self.addQueueColumn(_("Name"), 1)
        self.addQueueColumn(_("Category"), 2)
        self.addQueueColumn(_("Size"), 3)
        self.addQueueColumnProgressBar(_("Progress"), 4, 5)
        
        self.mainStatusMenu = self.glade.get_widget("StatusMenu")
        
        # Now we connect the menu to the statusIcon
        self.mainStatusIcon.connect("popup-menu", self.showMenu, self.mainStatusMenu)
        self.mainStatusIcon.connect("activate", self.mainWindowHider)
        
        self.categories = [_("Music"), _("DVD Movie"), _("XVID Movie"), _("TV Series"), _("HD Movie"), _("Game"), _("Software"), _("Other")]
        
        # Initialize the file selection dialog
        self.addFileDialog = self.glade.get_widget("AddFileDialog")
        self.addFileName = self.glade.get_widget("AddFileName")
        self.addFileTable = self.glade.get_widget("AddFileTable")
        
        self.glade.signal_autoconnect({
            "on_AddFileDialog_selection_changed"    : self.changeFileName,
            "on_AddDialogCancelButton_clicked"      : self.hideAddFileDialog,
            "on_AddDialogAddButton_clicked"         : self.fileAdder
        })
        
        self.addFileCategory = gtk.combo_box_new_text()
        
        for category in self.categories:
            self.addFileCategory.append_text(category)
        
        self.addFileCategory.set_active(7)
        self.addFileCategory.show()
        
        self.addFileTable.attach(self.addFileCategory, 1, 2, 1, 2)
        
        self.addFileFilter = gtk.FileFilter()
        self.addFileFilter.add_pattern("*.nzb")
        self.addFileFilter.add_pattern("*.NZB")
        self.addFileDialog.set_filter(self.addFileFilter)
        
        # Initialize the "About" window
        self.aboutDialog = self.glade.get_widget("AboutDialog")
        self.aboutDialog.connect("response", self.closeAboutDialog)
    
    def mainWindowHider(self, widget, void=None):
        if self.mainWindowShow:
            self.mainWindow.hide()
            self.mainWindowShow = 0
        else:
            self.mainWindow.show()
            self.mainWindowShow = 1
        
        return True
            
    
    def showMenu(self, status_icon, button, activate_time, menu):
        self.mainStatusMenu.popup(None, None, gtk.status_icon_position_menu, button, activate_time, status_icon)

    def addQueueColumn(self, title, columnID):
        column = gtk.TreeViewColumn(title, gtk.CellRendererText(), text=columnID)
        column.set_resizable(True)
        column.set_expand(True)
        self.queueTree.append_column(column)
    
    def addQueueColumnProgressBar(self, title, columnID, progress):
        column = gtk.TreeViewColumn(title, gtk.CellRendererProgress(), text=columnID, value=progress)
        column.set_resizable(False)
        column.set_expand(False)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(200)
        self.queueTree.append_column(column)
        
    def delete_event(self, widget, event):
        self.running = 0
        return True
    
    def destroy(self, void):
        Prefs.lotta["window_height"] = self.mainWindow.get_size()[1]
        Prefs.lotta["window_width"] = self.mainWindow.get_size()[0]
        Prefs.lotta.save()
        
        self.mainWindow.hide()
        self.running = 0
        gtk.main_quit()
        self.backend.quit()

    def run(self):
        while self.running:
            if self.backend.running:
                self.backend.updateStatus()
                
                if self.backend.running == 2:
                    self.warningScreen()
                    self.backend.running = 0
                
                elif not self.backend.downloading == []:
                    self.mainToolBarPause.set_active(self.backend.paused)
                    self.mainSpeedLabel.set_text(_("%s KB/s") % (self.backend.speed))
                    self.mainRemainingLabel.set_text(_("Remaining: %s MB") % (self.backend.remaining) +  " - " + self.backend.eta)
                
                else:
                    self.mainSpeedLabel.set_text(_("None"))
                    self.mainRemainingLabel.set_markup(_("None"))
                
                sleep(Prefs.lotta["sleep_time"])
            else:
                self.running = 0
    
    def moveDown(self, void):
        try:
            selection = self.queueTree.get_selection()
            model, selection_iter = selection.get_selected()
            self.backend.moveDown(selection_iter)
        except:
            logging.error(_("Could not move items."))
    
    def moveUp(self, void):
        try:    
            selection = self.queueTree.get_selection()
            model, selection_iter = selection.get_selected()
            self.backend.moveUp(selection_iter)
        except:
            logging.error(_("Could not move items."))
    
    def clearFinished(self, void):
        self.backend.clearFinished()
    
    def togglePause(self, void):
        if self.mainToolBarPause.get_active():
            self.backend.pause()
        else:
            self.backend.resume()
    
    def delFile(self, void):
        selection = self.queueTree.get_selection()
        model, selection_iter = selection.get_selected()
        if selection_iter:
            dialog = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, buttons=gtk.BUTTONS_OK_CANCEL, type=gtk.MESSAGE_QUESTION, message_format="Are you sure you want to cancel this download?")
            response = dialog.run()
            dialog.destroy()
            
            if response == gtk.RESPONSE_OK:
                try:
                    self.backend.delFile(selection_iter)
                except:
                    logging.error(_("Could not delete item."))
    
    def addFile(self, widget, input=None):
        if not input == None:
            try:
                self.addFileDialog.select_filename(input)
            except:
                logging.error(_("Could not set the filename."))
        
        
        self.addFileDialog.run()
    
    def fileAdder(self, widget):
        files = self.addFileDialog.get_filenames()
        
        if files:
            for file in files:
                if not os.path.isdir(file):
                    category = self.addFileCategory.get_active_text()
                        
                    if len(files) == 1:
                        name = self.addFileName.get_text()
                    else:
                        name = file[:-4].split("/")[-1]
                    
                    move(file, paths.tempDir() + category + " -- " + name + ".nzb")
                    returnvalue = paths.tempDir() + category + " -- " + name + ".nzb"
                    self.backend.addFile(returnvalue)
                
                else:
                    self.addFileDialog.set_current_folder(self.addFileDialog.get_filename())
                
            self.addFileDialog.hide()
            
    def hideAddFileDialog(self, widget):
        self.addFileDialog.hide()
    
    def changeFileName(self, widget):
        names = self.addFileDialog.get_filenames()
        
        if len(names) is 1:
            if names[0][-4:].lower() == ".nzb":
                names = names[0][:-4].split("/")[-1].replace("."," ").replace("_"," ")
                self.addFileName.set_text(names)
                self.addFileName.set_sensitive(True)  

        elif len(names) is not 0:
            self.addFileName.set_text("Selected multiple files")
            self.addFileName.set_sensitive(False)
            for name in names:
                if name[-4:].lower() == ".nzb":
                    name = name[:-4].split("/")[-1].replace("."," ").replace("_"," ")
                    
        else:
            self.addFileName.set_text("")
            
    def dragFile(self, treeview, context, x, y, selection, info, etime):
        data = selection.data
        data = data.replace('file://', "")
        # data = data.replace("\r\n", "")
        
        data = data.strip()
        
        if len(data.split()) == 1:
            file = data
            file = file.replace("%20", " ")
            file = file.strip()
            self.addFile("",file)
        else:
            for file in data.split():
                if file.lower().endswith(".nzb"):
                    file.replace("%20", " ")
                    file.strip()
                    self.backend.addFile(file)
        
        
            
                
    def about(self, widget):
        self.aboutDialog.show()
    
    def closeAboutDialog(self, widget, response):
        if response == gtk.RESPONSE_CANCEL:
            self.aboutDialog.hide()
    
    def warningScreen(self):
        warningDialog = self.glade.get_widget("WarningDialog")
        warningDialog.run()
        warningDialog.hide()
        self.mainWindow.destroy()
        gtk.main_quit()
        self.running = 0
        self.backend.quit()
    
    def showStandalonePreferences(self, *args):
        prefsgui.StandaloneModeDialog()
    
    def showFrontmodePreferences(self, *args):
        prefsgui.FrontModeDialog()
