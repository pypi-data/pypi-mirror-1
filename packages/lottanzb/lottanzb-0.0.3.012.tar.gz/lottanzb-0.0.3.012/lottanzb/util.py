import paths
import gtk, gtk.glade

class UITree(gtk.glade.XML):
    def __init__(self, root):
        self.root = root
        
        gtk.glade.XML.__init__(self, paths.dataDir("lottanzb.glade"), root)
    
    def get_widget_dict(self, widgets, root=""):
        dict = {}
        
        for widget in widgets:
            dict[widget.lower()] = self.get_widget((root or self.root) + widget)
        
        return dict
    
    def get_root_widget(self):
        return self.get_widget(self.root)

# From http://blog.toidinamai.de/python/singletons
class SingletonClass(type):
  singletons = {}

  def __call__(self, *args, **kwds):
    try:
      return self.singletons[self]
    except KeyError:
      self.singletons[self] = super(SingletonClass, self).__call__(*args, **kwds)
      return self.singletons[self]

class Singleton(object):
  __metaclass__ = SingletonClass
