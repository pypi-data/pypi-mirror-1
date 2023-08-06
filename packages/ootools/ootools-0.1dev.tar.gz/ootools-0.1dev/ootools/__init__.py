# OpenOffice utils.
#
# Based on code from:
#   PyODConverter (Python OpenDocument Converter) v1.0.0 - 2008-05-05
#   Copyright (C) 2008 Mirko Nasato <mirko@artofsolving.com>
#   Licensed under the GNU LGPL v2.1 - or any later version.
#   http://www.gnu.org/licenses/lgpl-2.1.html
#
"""
#OpenOffice, and openoffice.org-headless plugin needs to be installed.
#aptitude install openoffice.org-headless
#In python, simply create an instance of it and call connect() on that instance. Connect returns the OpenOffice desktop object.
oor     = ooutils.OORunner()
oodesktop = oor.connect()
# Do something with the "oodesktop"
"""
__all__ = ['OORunner'] 

import sys
import os
import time
import atexit


#OPENOFFICE_PORT = 8100

# Find OpenOffice.
#_oopaths=(
#        ('/usr/lib64/ooo-2.0/program',   '/usr/lib64/ooo-2.0/program'),
#        ('/opt/openoffice.org3/program', '/opt/openoffice.org/basis3.0/program'),
#        ('/usr/lib/openoffice/program', '/usr/lib/openoffice/program'), #Debian
#     )

#for p in _oopaths:
#    if os.path.exists(p[0]):
#        OPENOFFICE_PATH    = p[0]
#        OPENOFFICE_BIN     = os.path.join(OPENOFFICE_PATH, 'soffice')
#        OPENOFFICE_LIBPATH = p[1]

        # Add to path so we can find uno.
#        if sys.path.count(OPENOFFICE_LIBPATH) == 0:
#            sys.path.insert(0, OPENOFFICE_LIBPATH)
#        break


#import uno
#from com.sun.star.beans import PropertyValue
#from com.sun.star.connection import NoConnectException


class OORunner:
    """
    Start, stop, and connect to OpenOffice.
    """
    def __init__(self, port=None,path=None):
        """ Create OORunner that connects on the specified port. """
        if not port:
            port= 8100
        #print port 
        print path 
        if not path:
            # Find OpenOffice.
            _oopaths=(
                    ('/usr/lib64/ooo-2.0/program',   '/usr/lib64/ooo-2.0/program'),
                    ('/opt/openoffice.org3/program', '/opt/openoffice.org/basis3.0/program'),
                    ('/usr/lib/openoffice/program', '/usr/lib/openoffice/program'), #Debian
                 )
        else:
            _oopaths=((path,path))
        path_ok=False
        for p in _oopaths:
            if os.path.exists(p[0]):
                path_ok=True
                self.OPENOFFICE_PATH    = p[0]
                self.OPENOFFICE_BIN     = os.path.join(self.OPENOFFICE_PATH, 'soffice')
                self.OPENOFFICE_LIBPATH = p[1]
        
                # Add to path so we can find uno.
                if sys.path.count(self.OPENOFFICE_LIBPATH) == 0:
                    sys.path.insert(0, self.OPENOFFICE_LIBPATH)
                break
        if not path_ok:
            sys.exit('Path to OpenOffice program is not valid.')
        self.port = port
        import uno
        from com.sun.star.beans import PropertyValue
        from com.sun.star.connection import NoConnectException
        


    def connect(self, no_startup=False):
        """
        Connect to OpenOffice.
        If a connection cannot be established try to start OpenOffice.
        """
        import uno
        from com.sun.star.beans import PropertyValue
        from com.sun.star.connection import NoConnectException
        localContext = uno.getComponentContext()
        resolver     = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext)
        context      = None
        did_start    = False

        n = 0
        while n < 6:
            try:
                context = resolver.resolve("uno:socket,host=localhost,port=%d;urp;StarOffice.ComponentContext" % self.port)
                break
            except NoConnectException:
                pass

            # If first connect failed then try starting OpenOffice.
            if n == 0:
                # Exit loop if startup not desired.
                if no_startup:
                     break
                self.start()
                did_start = True

            # Pause and try again to connect
            time.sleep(1)
            n += 1

        if not context:
            raise Exception, "Failed to connect to OpenOffice on port %d" % self.port
        desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)

        if not desktop:
            raise Exception, "Failed to create OpenOffice desktop on port %d" % self.port

        if did_start:
            _started_desktops[self.port] = desktop

        return desktop


    def start(self):
        """
        Start a headless instance of OpenOffice.
        """
        args = [self.OPENOFFICE_BIN,
                '"-accept=socket,host=localhost,port=%d;urp;StarOffice.ServiceManager"' % self.port,
                '-norestore',
                '-nofirststartwizard',
                '-nologo',
                '-headless',
                ]
        env  = {'PATH'       : '/bin:/usr/bin:%s' % self.OPENOFFICE_PATH,
                'PYTHONPATH' : self.OPENOFFICE_LIBPATH,
                }

        try:
            #print args
            #pid = os.spawnve(os.P_NOWAIT, args[0], args, env)
            #print pid
            from subprocess import Popen,PIPE
            p=Popen([' '.join(list(args))],env=env,shell=True,stdout=PIPE)
            print 'OO Started'
        except Exception, e:
            raise Exception, "Failed to start OpenOffice on port %d, Error: %s" % (self.port, e.message)
        #if pid <= 0:
        #    raise Exception, "Failed to start OpenOffice on port %d" % self.port
        time.sleep(3)


    def stop(self):
        """
        Shutdown OpenOffice.
        """
        import uno
        from com.sun.star.beans import PropertyValue
        from com.sun.star.connection import NoConnectException
        local    = uno.getComponentContext()
        resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
        context  = resolver.resolve("uno:socket,host=localhost,port=%d;urp;StarOffice.ComponentContext" %self.port)
        desktop  = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
        desktop.terminate()
        print "OO Shutdown"

        #try:
        #    if _started_desktops.get(self.port):
        #        _started_desktops[self.port].terminate()
        #        del _started_desktops[self.port]
        #except Exception, e:
        #    pass



# Keep track of started desktops and shut them down on exit.
_started_desktops = {}

def _shutdown_desktops():
    """ Shutdown all OpenOffice desktops that were started by the program. """
    for port, desktop in _started_desktops.items():
        try:
            if desktop:
                desktop.terminate()
        except Exception, e:
            pass


atexit.register(_shutdown_desktops)


def oo_shutdown_if_running(port=None):
    """ Shutdown OpenOffice if it's running on the specified port. """
    if not port:
        port=8100 
    oorunner = OORunner(port)
    try:
        desktop = oorunner.connect(no_startup=True)
        desktop.terminate()
    except Exception, e:
        pass


def oo_properties(**args):
    """
    Convert args to OpenOffice property values.
    """
    props = []
    for key in args:
        prop       = PropertyValue()
        prop.Name  = key
        prop.Value = args[key]
        props.append(prop)

    return tuple(props)

