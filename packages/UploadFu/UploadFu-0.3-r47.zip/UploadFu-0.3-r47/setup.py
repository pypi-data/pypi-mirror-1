import os
os.environ['HOME'] = os.getcwd()
print os.environ['HOME']
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
#~ from distutils.core import setup
setup(
    name = "UploadFu",
    version = "0.3",
    author="Leonord",
    author_email="allegory.bucket@gmail.com",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
    ],      
    description="Bittorrent upload tools for win32",
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
    install_requires = ['mechanize>=0.1.7b', 'configobj>=4.4.0', 'pywin32'],
    packages=['uploadfu', 'uploadfu.BitTorrent'],
    
    zip_safe=False,
  
)