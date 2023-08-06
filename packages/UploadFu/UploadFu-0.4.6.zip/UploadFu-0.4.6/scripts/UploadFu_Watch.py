import os
import sys
import time
import glob

import win32con
import win32file
import winnt
import win32process
import logging

from uploadfu import get_work_dir, set_logging
PYTHON_PATH, WORK_DIR = get_work_dir()
set_logging(WORK_DIR)
logger = logging.getLogger("watcher")


try:
    assert len(sys.argv) >= 3
    path_to_watch = os.path.abspath (sys.argv[2])
    ini_file = os.path.abspath (sys.argv[1])
    delay = len(sys.argv)>3 and sys.argv[3] or '0'
    console = len(sys.argv)>4 and sys.argv[4] or 'y'
    console = True if console.lower() in ('y','yes','true') else False
except:
    print "Usage: %s ini_file path_to_watch [delay] [console]" % os.path.basename(sys.argv[0])
    
    sys.exit(1)

file(os.path.join(WORK_DIR, "%s.pid"%win32process.GetCurrentProcessId()), 'w').write('\n'.join((ini_file, path_to_watch, delay)))
delay = int(delay)
    
hDir = win32file.CreateFile(
    path_to_watch,
    win32con.GENERIC_READ,
    win32con.FILE_SHARE_READ|win32con.FILE_SHARE_WRITE,
    None,
    win32con.OPEN_EXISTING,
    win32con.FILE_FLAG_BACKUP_SEMANTICS,
    None
)
while 1:   
    events = win32file.ReadDirectoryChangesW(
        hDir, 1024, False, 
        win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
        win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
        win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
        win32con.FILE_NOTIFY_CHANGE_SIZE |
        win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
        win32con.FILE_NOTIFY_CHANGE_SECURITY,
        None,
        None
    )
    for id, path in events:
        cpath = os.path.join(path_to_watch, path)
        if id == winnt.FILE_ACTION_ADDED:
            if os.path.isdir(cpath):
                logger.info("Detected %s." % cpath)
                time.sleep(delay)
                command = u'cmd /c start /min "%spython%s.exe" "%s" "%s" %s' % (PYTHON_PATH, '' if console else 'w', os.path.join(WORK_DIR, 'UploadFu_Upload.py'), ini_file, cpath)
                logger.info("Running %s" % repr(command))
                startup_info = win32process.STARTUPINFO()
                win32process.CreateProcess(None, command, None, None, 0, 0, None, None, startup_info)
            
                #~ shutil.copytree(cpath, rpath)
