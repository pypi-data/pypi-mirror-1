import os
os.environ['HOME'] = os.getcwd()
print os.environ['HOME']
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
import uploadfu
name, version = uploadfu.__version__.split()
setup(
    name = name,
    version = version,
    author="Leonord",
    author_email="allegory.bucket@gmail.com",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
    ],      
    description="Bittorrent upload tools for win32",
    scripts = ['scripts/UploadFu_Upload.py', 'scripts/UploadFu_Watch.py', 'scripts/UploadFu_ContextMenu.py', 'iplay.ini'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['mechanize>=0.1.7b', 'configobj>=4.4.0'],
    packages=['uploadfu', 'uploadfu.BitTorrent'],
    
    zip_safe=False,
  
)