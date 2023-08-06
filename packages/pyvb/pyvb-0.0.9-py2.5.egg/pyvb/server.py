"""server - Holds abstractions that represent different server types."""
import pkg_resources
from pyvb import *
from turbogears import controllers, start_server, config, expose
import simplejson

class vbRestListController(controllers.Controller):
    def __init__(self, vb):
        self.vb=vb
    
    @expose()
    def index(self):
        return "/list"
    
    @expose()
    def vms(self):
        result=[]
        for i in self.vb.listVMS():
            result.append(i.__dict__)
        return simplejson.dumps(result)
    
    @expose()
    def ostypes(self):
        result=[]
        for i in self.vb.listOsTypes():
            result.append(i.__dict__)
        return simplejson.dumps(result)
    
    @expose()
    def hostdvds(self):
        result=[]
        for i in self.vb.listHostDvds():
            result.append(i.__dict__)
        return simplejson.dumps(result)
    
    @expose()
    def dvds(self):
        result=[]
        for i in self.vb.listDvds():
            result.append(i.__dict__)
        return simplejson.dumps(result)
    
    @expose()
    def hdds(self):
        result=[]
        for i in self.vb.listHdds():
            result.append(i.__dict__)
        return simplejson.dumps(result)
    
class vbRestGetController(controllers.Controller):
    def __init__(self, vb):
        self.vb=vb
    
    @expose()
    def index(self):
        return "/get"
    
    @expose()
    def vm(self, *args, **kw):
        return simplejson.dumps(self.vb.getVM(args[0]).__dict__)
    
    @expose()
    def hdd(self, *args, **kw):
        return simplejson.dumps(self.vb.getHDD(args[0]).__dict__)
    
class vbRestVmController(controllers.Controller):
    def __init__(self, vb):
        self.vb=vb
        
    @expose()
    def index(self):
        return "/vm"
    
    @expose()
    def start(self, *args, **kw):
        try:
            type=args[1]
        except IndexError:
            type='gui'
        try:
            v=self.vb.getVM(args[0])
            self.vb.startVM(v, type=type)
            return simplejson.dumps(v.__dict__)
        except Exception,e:
            return simplejson.dumps(e.message)
        
    @expose()
    def poweroff(self, *args, **kw):
        try:
            v=self.vb.getVM(args[0])
            self.vb.poweroffVM(v)
            return simplejson.dumps(v.__dict__)
        except Exception,e:
            return simplejson.dumps(e.message)
        
    @expose()
    def acpipoweroff(self, *args, **kw):
        try:
            v=self.vb.getVM(args[0])
            self.vb.acpipoweroffVM(v)
            return simplejson.dumps(v.__dict__)
        except Exception,e:
            return simplejson.dumps(e.message)
        
    @expose()
    def pause(self, *args, **kw):
        try:
            v=self.vb.getVM(args[0])
            self.vb.pauseVM(v)
            return simplejson.dumps(v.__dict__)
        except Exception,e:
            return simplejson.dumps(e.message)
        
    @expose()
    def resume(self, *args, **kw):
        try:
            v=self.vb.getVM(args[0])
            self.vb.resumeVM(v)
            return simplejson.dumps(v.__dict__)
        except Exception,e:
            return simplejson.dumps(e.message)
    
class vbRestServer(controllers.RootController):
    def __init__(self):
        self.vb=vb.VB()
        self.list=vbRestListController(self.vb)
        self.get=vbRestGetController(self.vb)
        self.vm=vbRestVmController(self.vb)
        cfg={"server.environment":"production",\
             "server.socket_port":8080}
        config.update(cfg)
    
    def startServer(self):
        start_server(self)
        
    @expose()
    def index(self):
        return "%s <i>%s</i>"%\
        (pkg_resources.get_distribution('pyvb').version,\
        _("pyvb REST Server"))