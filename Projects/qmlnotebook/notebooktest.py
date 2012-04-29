
from PyQt4.QtCore import QUrl, QObject

from PyQt4.QtDeclarative import QDeclarativeView
from PyQt4.QtGui import QStandardItemModel,QStandardItem

class ModelWrapper:
    def __init__(self, fieldlist):
        self.rolenames = rn = {}
        self.roleids = ri = {}
        for n,f in enumerate(fieldlist):
            rid = n + 100
            rn[rid] = f
            ri[f] = rid
        self.model = mo = QStandardItemModel()
        mo.setRoleNames(rn)

    def mkitem(self, d):
        """ dict with field->value """        
        si = QStandardItem()
        for k,v in d.items():
            rid = self.roleids[k]
            si.setData(v, rid)
            
        return si

class NbController:        
    def addNode(self, p, styling = {}):
        v = p.v
        d = {"h" : v.h, "b" : v.b, "gnx" : v.gnx, "level" : p.level()}
        d.update(styling)
        self.gnxcache[v.gnx] = v    
        si = self.mw.mkitem(d )
        self.mw.model.appendRow(si)

    def add_all_nodes(self):
        for p in c.all_positions():                        
            self.addNode(p)
            
    def __init__(self):
        
        self.gnxcache = {}
        
        self.mw = ModelWrapper(["h", "b", "gnx", "level", "style"])

        self.add_all_nodes()       
        c._view = view = QDeclarativeView()
        ctx = view.rootContext()        
        
        ctx.setContextProperty("nodesModel", self.mw.model)
                
        path = g.os_path_join(g.computeLeoDir(), 'plugins', 'qmlnb', 'qml', 'leonbmain.qml')
        view.setSource(QUrl(path))
        view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        # Display the user interface and allow the user to interact with it.
        view.setGeometry(100, 100, 800, 600)
        view.show()
        
        c.dummy = view
        
NbController()        
