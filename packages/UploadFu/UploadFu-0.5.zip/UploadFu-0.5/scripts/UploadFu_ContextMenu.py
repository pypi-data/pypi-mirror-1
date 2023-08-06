# A sample context menu handler.
# Adds a 'Hello from Python' menu entry to .py files.  When clicked, a
# simple message box is displayed.
#
# To demostrate:
# * Execute this script to register the context menu.
# * Open Windows Explorer, and browse to a directory with a .py file.
# * Right-Click on a .py file - locate and click on 'Hello from Python' on
#   the context menu.
import pythoncom
from win32com.shell import shell, shellcon
import win32gui
import win32con
import win32api
import win32process
import win32gui_struct
import pywintypes
import glob
import string
import os
import sys
import _winreg
import logging

from configobj import ConfigObj
from uploadfu import get_work_dir, set_logging
PYTHON_PATH, WORK_DIR = get_work_dir()
set_logging(WORK_DIR)
logger = logging.getLogger("contextmenu")



IContextMenu_Methods = ["QueryContextMenu", "InvokeCommand", "GetCommandString"]
IShellExtInit_Methods = ["Initialize"]

class ShellExtension:
    _reg_progid_ = "Python.ShellExtension.UploadFuMenu"
    _reg_desc_ = "UploadFu Python Shell Extension (context menu)"
    _reg_clsid_ = "{F002336C-C9EE-4a7f-8D7F-C660393C381F}"
    _com_interfaces_ = [shell.IID_IShellExtInit, shell.IID_IContextMenu]
    _public_methods_ = IContextMenu_Methods + IShellExtInit_Methods

    def Initialize(t, folder, dataobj, hkey):
        print "Init", folder, dataobj, hkey
        t.dataobj = dataobj

    def QueryContextMenu(t, hMenu, indexMenu, idCmdFirst, idCmdLast, uFlags):
        
        print (hMenu, indexMenu, idCmdFirst, idCmdLast, uFlags)
        ID = idCmdFirst
        CMDS = 3
        format_etc = win32con.CF_HDROP, None, 1, -1, pythoncom.TYMED_HGLOBAL
        sm = t.dataobj.GetData(format_etc)
        num_files = shell.DragQueryFile(sm.data_handle, -1)
           
        
        
        t._handlers = {}
        t._unwatch = {}
        t._watch = {}
        hsubmenu = win32gui.CreatePopupMenu()
        hupload_submenu = win32gui.CreatePopupMenu()
        item, extras = win32gui_struct.PackMENUITEMINFO(text = "Upload %s torrents with ..." % num_files, wID=ID, hSubMenu = hupload_submenu)
        ID += 1
        win32gui.InsertMenuItem(hsubmenu, ID, 0, item)
        
        hwatch_submenu = win32gui.CreatePopupMenu()
        t._watch_dir = shell.DragQueryFile(sm.data_handle,0)
        item, extras = win32gui_struct.PackMENUITEMINFO(text = "Watch %s with ..." % os.path.basename(t._watch_dir), wID=ID, hSubMenu = hwatch_submenu)
        ID += 1
        win32gui.InsertMenuItem(hsubmenu, ID, 1, item)
            
        hunwatch_submenu = win32gui.CreatePopupMenu()
        item, extras = win32gui_struct.PackMENUITEMINFO(text = "Unwatch", wID=ID, hSubMenu = hunwatch_submenu)
        ID += 1
        win32gui.InsertMenuItem(hsubmenu, ID, 1, item)
        
        for id, pidfile in enumerate(glob.glob(os.path.join(WORK_DIR, '*.pid'))):
            pid = int(os.path.splitext(os.path.basename(pidfile))[0])
            try:
                hProcess = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, pid)
            except pywintypes.error, e:
                os.unlink(pidfile)
                hProcess = None
            #~ win32api.TerminateProcess(hProcess,0)
            #~ win32api.CloseHandle(hProcess)
            if hProcess:
                try:
                    ini, watchdir, delay = filter(None,map(string.strip,file(pidfile).readlines()))
                except:
                    continue
                item, extras = win32gui_struct.PackMENUITEMINFO(text = "%s [%s]" % (watchdir, os.path.basename(ini)), wID=ID)
                ID += 1
                win32gui.InsertMenuItem(hunwatch_submenu, CMDS, 1, item)
                t._unwatch[CMDS] = (hProcess, pidfile)
                CMDS += 1
            else:
                pass
        
        #~ [
        for id, conf_file in enumerate(glob.glob(os.path.join(WORK_DIR, '*.ini'))):
            conf_filename = os.path.basename(conf_file)
            try:
                config = ConfigObj(os.path.join(WORK_DIR, conf_file), unrepr=True, interpolation="Template")
            except:
                logging.exception("We have a bad config file: %s" % conf_filename)
                config = {'name': 'ERROR IN: %s' % conf_filename}
            logger.info('Adding: %s' % conf_file)
            item, extras = win32gui_struct.PackMENUITEMINFO(text = config['name'], wID=ID)
            ID += 1
            win32gui.InsertMenuItem(hupload_submenu, id, 1, item)
            t._handlers[CMDS] = conf_file
            CMDS += 1
            delay = config.get('watcher_sleep', 0)
            console = config.get('watch_upload_console', False)
            item, extras = win32gui_struct.PackMENUITEMINFO(text = "%s [%ss delay]" % (config['name'], delay), wID=ID)
            ID += 1
            win32gui.InsertMenuItem(hwatch_submenu, id, 1, item)
            t._watch[CMDS] = (conf_file, delay, console)
            CMDS += 1

        item, extras = win32gui_struct.PackMENUITEMINFO(hSubMenu = hsubmenu, wID=ID, text = "UploadFu")
        ID += 1
        win32gui.InsertMenuItem( hMenu, indexMenu, 1, item)
        indexMenu += 1
        return ID - idCmdFirst

    def InvokeCommand(t, ci):
        print '>>>', ci
        mask, hwnd, verb, params, dir, nShow, hotkey, hicon = ci
        if verb >> 16:
            # This is a textual verb invocation... not supported.
            return 0
        print '---', t._handlers
        print '---', t._watch
        print '---', t._unwatch
        print '---', verb
        if verb in t._handlers:
            startup_info = win32process.STARTUPINFO()
                
            format_etc = win32con.CF_HDROP, None, 1, -1, pythoncom.TYMED_HGLOBAL
            sm = t.dataobj.GetData(format_etc)
            num_files = shell.DragQueryFile(sm.data_handle, -1)
            selected_files = []
            for i in xrange(num_files):
                selected_files.append(u'"%s"' % shell.DragQueryFile(sm.data_handle, i).decode('iso-8859-1'))
            command = u'"%spython.exe" "%s" "%s" %s' % (PYTHON_PATH, os.path.join(WORK_DIR, 'UploadFu_Upload.py'), os.path.join(WORK_DIR, t._handlers[verb]), ' '.join(selected_files))
            logger.info("Running %s" % repr(command))
            win32process.CreateProcess(None, command, None, None, 0, 0, None, None, startup_info)
        elif verb in t._watch:
            startup_info = win32process.STARTUPINFO()
            ini, delay, console = t._watch[verb]
            command = u'"%spythonw.exe" "%s" "%s" "%s" %s %s' % (PYTHON_PATH, os.path.join(WORK_DIR, 'UploadFu_Watch.py'), os.path.join(WORK_DIR, ini), t._watch_dir, delay, console)
            logger.info("Running %s"% repr(command))
            win32process.CreateProcess(None, command, None, None, 0, 0, None, None, startup_info)
        elif verb in t._unwatch:
            hProcess, pidfile = t._unwatch[verb]
            win32api.TerminateProcess(hProcess,0)
            win32api.CloseHandle(hProcess)
            os.unlink(pidfile)
        else:
            logger.error("Unsupported command id %i!" % verb)
            raise Exception("Unsupported command id %i!" % verb)
            
    def GetCommandString(t, cmd, uFlags):
        if uFlags & shellcon.GCS_VALIDATEA or uFlags & shellcon.GCS_VALIDATEW:
            if cmd in t._handlers:
                return 1
            return 0
        if uFlags & shellcon.GCS_VERBA or uFlags & shellcon.GCS_VERBW:
            return 0
        if uFlags & shellcon.GCS_HELPTEXTA or uFlags & shellcon.GCS_HELPTEXTW:
            # The win32com.shell implementation encodes the resultant
            # string into the correct encoding depending on the flags.
            return t._handlers[cmd]
        return 0
        
def DllRegisterServer():
    import _winreg
    key = _winreg.CreateKey(_winreg.HKEY_CLASSES_ROOT,
                            "Directory\\shellex")
    subkey = _winreg.CreateKey(key, "ContextMenuHandlers")
    subkey2 = _winreg.CreateKey(subkey, "UploadFu")
    _winreg.SetValueEx(subkey2, None, 0, _winreg.REG_SZ, ShellExtension._reg_clsid_)
    print ShellExtension._reg_desc_, "registration complete."

def DllUnregisterServer():
    import _winreg
    try:
        key = _winreg.DeleteKey(_winreg.HKEY_CLASSES_ROOT,
                                "Directory\\shellex\\ContextMenuHandlers\\UploadFu")
    except WindowsError, details:
        import errno
        if details.errno != errno.ENOENT:
            raise
    print ShellExtension._reg_desc_, "unregistration complete."

if __name__=='__main__':
    from win32com.server import register
    register.UseCommandLine(ShellExtension,
                   finalize_register = DllRegisterServer,
                   finalize_unregister = DllUnregisterServer)
