"""server - Holds abstractions that represent different server types."""
import pkg_resources
from pyvb import *
from turbogears import controllers, start_server, config, expose
import simplejson

class vbRestListController(controllers.Controller):
    """REST controllers for listing operations."""
    def __init__(self, vb):
        self.vb=vb
    
    @expose()
    def index(self):
        """Default index controller.
        @return:  The current controller path.
        @rtype: String"""
        return "/list"
    
    @expose()
    def vms(self):
        """Return a JSON list of virtual machines.
        @return: A JSON list of virtual machines.
        @rtype: String"""
        result=[]
        for i in self.vb.listVMS():
            result.append(i.__dict__)
        return simplejson.dumps(result)
    
    @expose()
    def ostypes(self):
        """Return a JSON list of operating system types.
        @return: A JSON list of operating system types.
        @rtype: String"""
        result=[]
        for i in self.vb.listOsTypes():
            result.append(i.__dict__)
        return simplejson.dumps(result)
    
    @expose()
    def hostdvds(self):
        """Return a JSON list of host DVDs.
        @return: A JSON list of host DVDs.
        @rtype: String"""
        result=[]
        for i in self.vb.listHostDvds():
            result.append(i.__dict__)
        return simplejson.dumps(result)
    
    @expose()
    def dvds(self):
        """Return a JSON list of virtual DVDs.
        @return: A JSON list of virtual DVDs.
        @rtype: String"""
        result=[]
        for i in self.vb.listDvds():
            result.append(i.__dict__)
        return simplejson.dumps(result)
    
    @expose()
    def hdds(self):
        """Return a JSON list of HDDs.
        @return: A JSON list of HDDs.
        @rtype: String"""
        result=[]
        for i in self.vb.listHdds():
            result.append(i.__dict__)
        return simplejson.dumps(result)
    
class vbRestGetController(controllers.Controller):
    """REST controller for get operations."""
    def __init__(self, vb):
        """Constructor.  Initialize the VirtualBox class.
        @param vb: The VirtualBox hypervisor abstraction.
        @type vb: L{pyvb.vb.VB}
        @return: A new L{pyvb.server.vbRestGetController}.
        @rtype: L{pyvb.server.vbRestGetController}"""
        self.vb=vb
    
    @expose()
    def index(self):
        """The default index controller.
        @return: The current controller path.
        @rtype: String"""
        return "/get"
    
    @expose()
    def vm(self, *args, **kw):
        """Return the JSON representation of the specified VM.
        The request should take the follwing form::
            <host>/get/vm/<uuid>
        @return: A JSON representation of the specified VM.
        @rtype: String"""
        return simplejson.dumps(self.vb.getVM(args[0]).__dict__)
    
    @expose()
    def hdd(self, *args, **kw):
        """Return the JSON representation of the specified HDD.
        The request should take the following form::
            <host>/get/hdd/<uuid>
        @return: A JSON representation of the specified VM.
        @rtype: String"""
        return simplejson.dumps(self.vb.getHDD(args[0]).__dict__)
    
class vbRestVmController(controllers.Controller):
    """REST controller for VM operations."""
    def __init__(self, vb):
        """Constructor.  Initialize the VirtualBox class.
        @param vb: The VirtualBox hypervisor abstraction.
        @type vb: L{pyvb.vb.VB}
        @return: A new L{pyvb.server.vbRestVmController} instance.
        @rtype: L{pyvb.server.vbRestVmController}"""
        self.vb=vb
        
    @expose()
    def index(self):
        """The default index controller.
        @return: The current controller path.
        @rtype: String"""
        return "/vm"
    
    @expose()
    def start(self, *args, **kw):
        """Start the specified VM and return a JSON representation
        of the VM.  The request should take the following form::
            <host>/vm/start/<uuid>
        @return: The JSON representation of the specified VM.
        @rtype: String"""
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
        """Poweroff the specified VM and return a JSON representation
        of the VM.  The request should take the following form::
            <host>/vm/poweroff/<uuid>
        @return: The JSON representation of the specified VM.
        @rtype: String"""
        try:
            v=self.vb.getVM(args[0])
            self.vb.poweroffVM(v)
            return simplejson.dumps(v.__dict__)
        except Exception,e:
            return simplejson.dumps(e.message)
        
    @expose()
    def acpipoweroff(self, *args, **kw):
        """ACPI poweroff the specified VM and return a JSON representation
        of the VM.  The request should take the following form::
            <host>/vm/acpipoweroff/<uuid>
        @return: The JSON representation of the specified VM.
        @rtype: String"""
        try:
            v=self.vb.getVM(args[0])
            self.vb.acpipoweroffVM(v)
            return simplejson.dumps(v.__dict__)
        except Exception,e:
            return simplejson.dumps(e.message)
        
    @expose()
    def pause(self, *args, **kw):
        """Pause the specified VM and return a JSON representation
        of the VM.  The request should take the following form::
            <host>/vm/pause/<uuid>
        @return: The JSON representation of the specified VM.
        @rtype: String"""
        try:
            v=self.vb.getVM(args[0])
            self.vb.pauseVM(v)
            return simplejson.dumps(v.__dict__)
        except Exception,e:
            return simplejson.dumps(e.message)
        
    @expose()
    def resume(self, *args, **kw):
        """Resume the specified VM and return a JSON representation
        of the VM.  The request should take the following form::
            <host>/vm/resume/<uuid>
        @return: The JSON representation of the specified VM.
        @rtype: String"""
        try:
            v=self.vb.getVM(args[0])
            self.vb.resumeVM(v)
            return simplejson.dumps(v.__dict__)
        except Exception,e:
            return simplejson.dumps(e.message)
    
class vbRestServer(controllers.RootController):
    """A basic REST server for carrying out VirtalBox actions."""
    def __init__(self, environment='production', port=8080):
        """Constructor.  Initialize the VirtualBox hypervisor abstraction,
        the REST controllers, and the turbogears HTTP server.
        @keyword environment: The server environment.
        @type environment: String
        @keyword port: The server port.
        @type port: Integer.
        @return: A new L{pyvb.server.vbRestServer} instance.
        @rtype: L{pyvb.server.vbRestServer}"""
        self.vb=vb.VB()
        self.list=vbRestListController(self.vb)
        self.get=vbRestGetController(self.vb)
        self.vm=vbRestVmController(self.vb)
        cfg={"server.environment":environment,\
             "server.socket_port":port}
        config.update(cfg)
    
    def startServer(self):
        """Start the REST server.
        @return: None
        @rtype: None"""
        start_server(self)
        
    @expose()
    def index(self):
        """The default index controller.
        @return: The pyvb version.
        @rtype: String"""
        return "%s <i>%s</i>"%\
        (pkg_resources.get_distribution('pyvb').version,\
        _("pyvb REST Server"))