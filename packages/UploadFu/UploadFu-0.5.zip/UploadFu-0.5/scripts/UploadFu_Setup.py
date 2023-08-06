import subprocess, os, uploadfu
PYTHON_PATH, WORK_DIR = uploadfu.get_work_dir()
os.chdir(WORK_DIR)
subprocess.call("UploadFu_Setup.bat")
print 'Done.'


