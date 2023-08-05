import sys
import os

from configobj import ConfigObj


from uploadfu import get_work_dir, upload

PYTHON_PATH, WORK_DIR = get_work_dir()

if __name__ == "__main__":
    from win32com.shell import shell, shellcon
    import _winreg as wr
    import win32gui
    def BrowseCallbackProc(hwnd, msg, lp, data):
        if msg== shellcon.BFFM_INITIALIZED:
            win32gui.SendMessage(hwnd, shellcon.BFFM_SETSELECTION, 1, data)

    if len(sys.argv) >= 3:
        try:
            #~ print "play(",sys.argv[1], sys.argv[2] 
            upload(sys.argv[1], sys.argv[2:], WORK_DIR)
        except:
            import traceback
            traceback.print_exc()
        raw_input("Press enter")
    else:
        print "No or bad arguments. "
        print "Usage is:"
        print "     %s config_file directory [directory [...]]" % sys.argv[0]
        print 
        print "     - the directory will be uploaded according to config files."
        raw_input("Press enter")
        
        program_name = "UploadFu"
    
        sh = wr.OpenKey(wr.HKEY_LOCAL_MACHINE, r'Software\Classes\Directory\shell', 0, wr.KEY_ALL_ACCESS)
        pos = 0
        while 1:
            try:
                subkey = wr.EnumKey(sh, pos)
                print subkey 
            except:
                break
            if subkey.startswith(program_name):
                wr.DeleteKey(sh, '%s\\command'%subkey)
                wr.DeleteKey(sh, subkey)
            else:
                pos += 1
        
                
        #~ for conf_file in glob.glob('*.ini'):
            #~ print "Creating %s for %s." % (program_name, conf_file)
            #~ tracker_name = ConfigObj(conf_file)['name']
            #~ cmdkey = wr.CreateKey(sh, '%s.%s' % (program_name,conf_file))
            #~ wr.SetValueEx(cmdkey, '', 0, wr.REG_SZ, "%s: %s" % (program_name,tracker_name)) 
            #~ wr.SetValueEx(wr.CreateKey(cmdkey, 'command'), '', 0, wr.REG_SZ, 'cmd /c %s %s "%%1"'%(os.path.abspath(sys.argv[0]), conf_file))
        

        #~ win32gui.MessageBox(0, "Setup DONE.", program_name, 0) 