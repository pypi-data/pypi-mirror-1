#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from __future__ import with_statement
import pkg_resources
import win32serviceutil
import win32service
import win32event
import sys
import os
import re
import getopt
import ConfigParser


def getServiceClassString(o, argv):
    return win32serviceutil.GetServiceClassString(o,argv)


class ServiceSettings():
    _wssection_ = "winservice"
    
    def __init__(self, cfg_file_name):
        c = ConfigParser.SafeConfigParser()
        c.read(cfg_file_name)
        self.cfg_file_name = cfg_file_name
        self.c = c
#        try:
#            c.get(self._wssection_,"svc_name")
#        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
#                raise Exception("No \"svc_name\" in the % section of %s" % (self._wssection_,cfg_file_name))
      
    def getCfgFileDir(self):
        return os.path.dirname(self.cfg_file_name)
        
    def getCfgFileName(self): #this filename is absolute
        return self.cfg_file_name
    
    def getSvcName(self):
        try:
            return self.c.get(self._wssection_,"svc_name")
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            return os.path.splitext(os.path.basename(self.cfg_file_name))[0]
    
    def getSvcDisplayName(self):
        try: 
            return self.c.get(self._wssection_,"svc_display_name")
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            return "%s Paste Service" % self.getSvcName()
    
    def getStdOutFileName(self):
        try:
            return self.c.get(self._wssection_,"log_file")
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            return os.path.join(self.getSvcName()+"_std.log")
    
    def getSvcDescription(self):
        try:
            desc = self.c.get(self._wssection_,"svc_description")+"; "
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            desc = ""
        return desc +"wsgi_ini_file: %s; log_file: %s"%(self.getCfgFileName(),self.getStdOutFileName())
    
    def getVirtualEnv(self):
        try:
            return self.c.get(self._wssection_,"virtual_env")
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            return None
    
    def transferEssential(self,o):
        o._svc_name_ = self.getSvcName()
        o._svc_display_name_ = self.getSvcDisplayName()
        o._svc_description_ = self.getSvcDescription() 

def getDescription(o,argv):
    try:
        desc = o._svc_description_
    except AttributeError:
        desc = ''
 
    return '%s Script: %s; Executable: %s ;.ini: %s' % (desc,os.path.abspath(argv[0]),sys.executable, getIniFileName(o) )

def checkIniFileName(file_name):
    if not os.path.exists(file_name):
        raise Exception( "The specified paster ini file ( %s ) doesn't exist. Correct the wsgi_ini_file attribute" % file_name)

def activate_virtualenv(ve_dir):
    import sys 
    import site 

    # Remember original sys.path.
    prev_sys_path = list(sys.path) 
    
    package_root = os.path.join(ve_dir,"lib","site-packages") 
    site.addsitedir(package_root)
    
    sys.real_prefix = sys.prefix
    sys.prefix = ve_dir

    # Reorder sys.path so new directories at the front.
    new_sys_path = [] 
    for item in list(sys.path): 
         if item not in prev_sys_path: 
            new_sys_path.append(item)
            pkg_resources.working_set.add_entry(item)  #doesn't seem to have any effect
            sys.path.remove(item) 
    sys.path[:0] = new_sys_path
    
    pkg_resources.working_set = pkg_resources.WorkingSet()

class PasteWinService(win32serviceutil.ServiceFramework):
    
    def __init__(self,args):
        self._svc_name_= args[0]
        self.ss = ServiceSettings(getCfgNameFromRegistry(self._svc_name_))
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcDoRun(self):
        
        if self.ss.getVirtualEnv():
            activate_virtualenv(self.ss.getVirtualEnv())

        os.chdir(self.ss.getCfgFileDir())

        from paste.script.serve import ServeCommand as Server
        s = Server(None)
        s.run([ self.ss.getCfgFileName() , '--log-file='+self.ss.getStdOutFileName() ] ) # --log-file redirects both stdout and stderr
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        sys.exit()

def getCfgNameFromRegistry(svc_name):
    return win32serviceutil.GetServiceCustomOption(svc_name,'wsgi_ini_file')

def custom_usage():
    print ""
    print "Option for wsgi deployments as windows services. This option is mandatory! :"
    print " -c config_file : the deployment ini file"

def usage():    
    try:
        win32serviceutil.HandleCommandLine(None,None,argv = [])
    except SystemExit, e:
        custom_usage()

def handle_command_line(argv):
    
    options_pattern = "c:n:"
    optlist,args = getopt.getopt(sys.argv[1:],options_pattern)
    
    cmd_cfg_file = None

    if len(args) == 1 and args[0] =='list':
        print "List of wsgi services (display names) installed: "
        print listServices()
        return
    
    if len(optlist)!=1 or optlist[0][1]=='':
        usage()
        return    
    
    if len(args) == 0:
        usage()
        return
    
    opt = optlist[0]
    if opt[0]=='-c':
        cmd_cfg_file = opt[1]
    else:
        print "Incorrect parameters"
        usage()
        return

    try:
        ds = ServiceSettings(os.path.abspath(cmd_cfg_file))
        class A():
            pass
        ds.transferEssential(A)
        win32serviceutil.HandleCommandLine(A, serviceClassString = getServiceClassString(PasteWinService , argv) ,argv = argv, customInstallOptions = options_pattern)
        win32serviceutil.SetServiceCustomOption(ds.getSvcName(),'wsgi_ini_file',os.path.abspath(cmd_cfg_file))
    except SystemExit, e:
        if e.code==1:
            custom_usage()

def listServices():
    import win32api
    import win32con
    import prettytable
    wsgi_svcs = prettytable.PrettyTable(["name","display name"])
    wsgi_svcs.set_field_align("name", "l")
    wsgi_svcs.set_field_align("display name", "l")
    services_key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "System\\CurrentControlSet\\Services")
    i = 0
    try:
        while 1:
            svc_name = win32api.RegEnumKey(services_key, i)
            try:
                params_key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "System\\CurrentControlSet\\Services\\"+svc_name+"\\Parameters")
                try:
                    wsgi_ini_file = win32api.RegQueryValueEx(params_key, 'wsgi_ini_file')[0]
                    main_svc_key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "System\\CurrentControlSet\\Services\\"+svc_name)
                    try:
                        pass
                        wsgi_svcs.add_row([svc_name,win32api.RegQueryValueEx(main_svc_key,'DisplayName')[0]])
                    except win32api.error:
                        pass
                    win32api.RegCloseKey(main_svc_key)
                except win32api.error:
                    pass
                win32api.RegCloseKey(params_key)
            except win32api.error:
                pass
            i = i + 1
    
    except:
        pass
    
    win32api.RegCloseKey(services_key)
    return str(wsgi_svcs)

def main():
    handle_command_line( argv = sys.argv)

if __name__=='__main__':
    main()
