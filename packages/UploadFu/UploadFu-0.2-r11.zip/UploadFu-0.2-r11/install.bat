setup.py install
echo import os;os.system(os.__file__.split('\\lib\\')[0]+'\\Scripts\\ContextMenu.py --unregister') | python -
echo import os;os.system(os.__file__.split('\\lib\\')[0]+'\\Scripts\\UploadFu_ContextMenu.py --unregister') | python -
echo import os;os.system(os.__file__.split('\\lib\\')[0]+'\\Scripts\\UploadFu_ContextMenu.py') | python -
pause