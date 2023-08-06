cd %~dp0
ez_setup.py mechanize configobj pywin32
easy_install -m uploadfu
pywin32_postinstall.py -install
ContextMenu.py --unregister
UploadFu_ContextMenu.py --unregister
UploadFu_ContextMenu.py
UploadFu_Upload.py silent
UploadFu_StartWatchJobs.py register
REM ~ pause