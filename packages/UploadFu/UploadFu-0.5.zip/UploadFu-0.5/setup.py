import os, sys
os.environ['HOME'] = os.getcwd()
print os.environ['HOME']
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
#~ from distutils.core import setup
setup(
    name = "UploadFu",
    version = "0.5",
    author="Leonord",
    author_email="allegory.bucket@gmail.com",
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
    ],      
    description="Bittorrent upload tools for win32",
    long_description="""
        This package features tools for batching torrent creation and automatic 
        upload to tbdev based trackers. It integrates in the windows folder's 
        context menu.
        
        Features
        --------
        
        - torrent creation and uploading according to configuration files
        - directory watching and automatic uploading of new files that are moved 
          there
        - a context menu to access all those fetures
        
        Notes
        -----
        
        - should work on linux just for the creation and upload part
        - requires pywin32 for rest of the stuff
    """,
    scripts = [
        'scripts/UploadFu_Upload.py', 
        'scripts/UploadFu_Watch.py', 
        'scripts/UploadFu_StartWatchJobs.py',
        'scripts/UploadFu_ContextMenu.py', 
        'scripts/UploadFu_example.ini', 
        'scripts/UploadFu_Setup.bat',
        'scripts/UploadFu_Setup.py',
        'ez_setup.py'
    ],
    options = {"bdist_wininst":
        {   
         "install_script": "UploadFu_Setup.py",
         "title": "UploadFu.win32",
        },
    },


    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['mechanize>=0.1.7b', 'configobj>=4.4.0'] + \
        (sys.platform == "win32" and ['pywin32'] or []),
    packages=['uploadfu', 'uploadfu.BitTorrent'],
    
    zip_safe=False,
  
)