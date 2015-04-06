#!/usr/bin/env python3

from optparse import OptionParser
import os
import subprocess
import sys
import uno
from com.sun.star.connection import NoConnectException

import time

port = 2002
css = "com.sun.star"
def trigger_open_new_file(f, present):
    if os.fork() == 0:
        cmdandargs = ['libreoffice', '--accept=socket,host=localhost,port=%d;urp;StarOffice.ServiceManager;tcpNoDelay=1' % port]
        if present:
            cmdandargs.append('--show')
        cmdandargs.append(f)
        subprocess.call(cmdandargs)
        sys.exit()

def trigger_close_old_file(f):
    if os.fork() == 0:
        time.sleep(2)
        localContext = uno.getComponentContext()
        servicemanager = localContext.ServiceManager
        resolver = servicemanager.createInstanceWithContext(css+'.bridge.UnoUrlResolver', localContext)
        context = None
        for attempt in range(50):
            try:
                context = resolver.resolve('uno:socket,host=localhost,port=%d;urp;StarOffice.ComponentContext' % port)
                break
            except NoConnectException:
                pass
            time.sleep(0.1)
        desktop = context.ServiceManager.createInstanceWithContext(css+'.frame.Desktop', context)
        component_enumeration = desktop.Components.createEnumeration()
        while(component_enumeration.hasMoreElements()):
            component = component_enumeration.nextElement()
            if component.Location == 'file://' + f and not component.isModified():
                    component.close(True)
                    os.unlink(f)
                    sys.exit()
        sys.exit()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-f', '--file', dest='filename',
            help='open file FILE with LibreOffice', metavar='FILE')
    parser.add_option('-o', '--oldfile', dest='oldfilename',
            help='old file to close in LibreOffice, if opened and unmodifed', metavar='OLDFILE')
    parser.add_option('-p', '--present', action='store_true', dest='present', default=False,
            help='open file in presentation mode')
    (options, args) = parser.parse_args()
    if(options.filename):
        trigger_open_new_file(options.filename, options.present)
    if(options.oldfilename):
        trigger_close_old_file(options.oldfilename)
