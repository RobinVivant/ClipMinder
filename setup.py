from setuptools import setup

APP = ['src/main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['PyQt6'],
    'includes': ['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
    'excludes': ['Carbon', 'tkinter'],
    'plist': {
        'CFBundleName': 'ClipMinder',
        'CFBundleDisplayName': 'ClipMinder',
        'CFBundleGetInfoString': "Monitors clipboard for file paths and processes them",
        'CFBundleIdentifier': "fr.vivant.robin",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
        'NSHumanReadableCopyright': u"Copyright © 2023, Robin Vivant, All Rights Reserved",
        'NSHighResolutionCapable': True,
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)