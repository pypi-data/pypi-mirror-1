import sys
import os
import logging

from configobj import ConfigObj


from uploadfu import get_work_dir, upload, set_logging

PYTHON_PATH, WORK_DIR = get_work_dir()
set_logging(WORK_DIR)
logger = logging.getLogger("uploadmain")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        try:
            #~ print "play(",sys.argv[1], sys.argv[2] 
            upload(sys.argv[1], sys.argv[2:], WORK_DIR)
        except:
            logger.exception("Booohooo ! upload() call failed:")
    else:
        print "No or bad arguments."
        print "Usage is:"
        print "     %s config_file directory [directory [...]]" % sys.argv[0]
        print 
        print "     - the directory will be uploaded according to config files."
        
        if sys.platform == 'win32':
            if not(len(sys.argv)>1 and sys.argv[1] == 'silent'): 
                raw_input("Press enter")
        
            program_name = "UploadFu"
        
            # cleanup some crap from older versions
            import _winreg as wr
            sh = wr.OpenKey(wr.HKEY_LOCAL_MACHINE, r'Software\Classes\Directory\shell', 0, wr.KEY_ALL_ACCESS)
            pos = 0
            while 1:
                try:
                    subkey = wr.EnumKey(sh, pos)
                except:
                    break
                if subkey.startswith(program_name):
                    wr.DeleteKey(sh, '%s\\command'%subkey)
                    wr.DeleteKey(sh, subkey)
                else:
                    pos += 1
