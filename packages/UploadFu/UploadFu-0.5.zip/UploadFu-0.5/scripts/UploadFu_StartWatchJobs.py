import sys
import os
import glob
import win32process
import win32api
import win32con
import pywintypes
import string
from configobj import ConfigObj


from uploadfu import get_work_dir, upload

PYTHON_PATH, WORK_DIR = get_work_dir()

if __name__ == "__main__":
    import _winreg as wr
    if len(sys.argv) != 2:
        print "Usage %s cmd" % sys.argv[0]
        print " cmd:"
        print "  register - register this script to start on boot"
        print "  start - start the jobs"
    else:
        if sys.argv[1] == 'register':
            key = wr.OpenKey(wr.HKEY_LOCAL_MACHINE, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, wr.KEY_ALL_ACCESS)
            wr.SetValueEx(key, 'UploadFu watch jobs start', 0, wr.REG_SZ, '%spythonw "%s%s" start' % (PYTHON_PATH, WORK_DIR, os.path.basename(sys.argv[0])))
        elif sys.argv[1] == 'start':
            jobs = []
            for pidfile in glob.glob(os.path.join(WORK_DIR, '*.pid')):
                pid = int(os.path.splitext(os.path.basename(pidfile))[0])
                try:
                    hProcess = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, pid)
                except pywintypes.error, e:
                    hProcess = None
                
                param = file(pidfile).readlines()    
                jobs.append(filter(None,map(string.strip,param)))
                os.unlink(pidfile)
                if hProcess:
                    print 'ALERT: watch job already running:', pid
                    print 'Terminating it.'
                    win32api.TerminateProcess(hProcess,0)
                    win32api.CloseHandle(hProcess)
                    
            for ini, watchdir, delay in jobs:
                startup_info = win32process.STARTUPINFO()
                command = u'"%spythonw.exe" "%s" "%s" "%s" %s' % (PYTHON_PATH, os.path.join(WORK_DIR, 'UploadFu_Watch.py'), os.path.join(WORK_DIR, ini), watchdir, delay)
                print "Running", repr(command)
                win32process.CreateProcess(None, command, None, None, 0, 0, None, None, startup_info)
                
                
        else:
            print "Wrong command"
            
        
                
        #~ for conf_file in glob.glob('*.ini'):
            #~ print "Creating %s for %s." % (program_name, conf_file)
            #~ tracker_name = ConfigObj(conf_file)['name']
            #~ cmdkey = wr.CreateKey(sh, '%s.%s' % (program_name,conf_file))
            #~ wr.SetValueEx(cmdkey, '', 0, wr.REG_SZ, "%s: %s" % (program_name,tracker_name)) 
            #~ wr.SetValueEx(wr.CreateKey(cmdkey, 'command'), '', 0, wr.REG_SZ, 'cmd /c %s %s "%%1"'%(os.path.abspath(sys.argv[0]), conf_file))
        

        #~ win32gui.MessageBox(0, "Setup DONE.", program_name, 0) 