# -*- coding: UTF-8 -*-
from setuptools import setup

setup(
    # metadata for upload to PyPI
    author = "Juergen Geuter",
    author_email = "tante@the-gay-bar.com",
    description = "Thinkwhack allows you to use your thinkpad's hdaps sensors to trigger actions.",
    license = "GNU GPL-3",
    keywords = "hdaps thinkpad",
    url = "http://the-gay-bar.com/thinkwhack/",   # project home page, if any
    download_url = "http://the-gay-bar.com/thinkwhack/dist/",
    
    # Actual project data
    name = "thinkwhack",
    version = "0.2",
    package_dir = {'thinkwhack':'src/thinkwhack'},
    packages = ['thinkwhack'],
    entry_points = {
        'gui_scripts': [
            'thinkwhack = thinkwhack:main',
            ],
        'setuptools.installation': [
            'eggsecutable = thinkwhack:main',
            ],
    },    
    
    data_files = [
        ('/usr/share/thinkwhack', ['share/trayicon_on.png','share/trayicon_off.png', 'share/defaults' ]),
        ],
)   
