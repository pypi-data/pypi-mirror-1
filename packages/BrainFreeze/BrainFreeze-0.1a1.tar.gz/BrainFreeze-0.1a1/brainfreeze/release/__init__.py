"""Release information and release tools"""

import os
from textwrap import dedent

# Define pypi release information
NAME = "BrainFreeze"
VERSION = "0.1a1"
DESCRIPTION = dedent("""
    BrainFreeze is an SQLAlchemy plugin for proxying properties on
    one-to-one related objects.  Kind of like SQLAlchemy's AssociationProxy,
    but for one-to-one relations instead of many-to-many relations.
""")
AUTHOR = "Ian Charnas, Brian Beck"
AUTHOR_EMAIL = "ian.charnas@gmail.com, exogen@gmail.com"
URL = "http://brainfreeze-alchemy.googlecode.com/"
DOWNLOAD_URL = "http://code.google.com/p/brainfreeze-alchemy/downloads/list"

# Add support for `python setup.py googlecode_upload`
#
# Note: This is not a very generalized way to do this, clearly I should be 
# using user_options instead of relying on some constants
GOOGLECODE_PROJECT = "brainfreeze-alchemy"

from distutils import log
from distutils.core import Command
from distutils.errors import DistutilsOptionError
from brainfreeze.release.googlecode_upload import upload_find_auth
class googlecode_upload(Command):
    """Setuptools Command to upload packages to google code"""
    description = "upload packages to google code"
    
    user_options = []
    
    def initialize_options(self):
        pass
        
    def finalize_options(self):
        pass

    def run(self):
        if not self.distribution.dist_files:
            raise DistutilsOptionError(
                "No dist file created in earlier command"
            )
        for command, pyversion, filename in self.distribution.dist_files:
            self.upload_file(command, pyversion, filename)
            
    def upload_file(self, command, pyversion, filename):
        command_filetype_map = {
            'bdist_egg': ("Python Egg", ['Type-Package', 'OpSys-All']),
            'bdist_msi': (
                "Microsoft Installer Package", 
                ['Type-Package', 'OpSys-Windows']
            ),
            'bdist_rpm': ("RPM", ['Type-Package', 'OpSys-Linux']),
            'bdist_wininst': (
                "Auto-Installing Executable for Microsoft Windows", 
                ['Type-Installer', 'OpSys-Windows']
            ),
            'sdist': ("Source Distribution", ['Type-Source', 'OpSys-All'])
        }
        
        self.announce("Submitting %s to Google Code" % filename, log.INFO)
        try:
            status, reason, url = upload_find_auth(
                filename, # file to upload
                GOOGLECODE_PROJECT, # which project to upload file to?
                command_filetype_map[command][0], # summary of file
                command_filetype_map[command][1] # labels for file
            )
            if url:
                self.announce(
                    "Google Code upload successful to URL: %s" % url
                )
            else:
                self.announce(
                    "Google Code upload failed.  Server said %s (%s)" %
                    (reason, status)
                )
        except Exception, e:
            self.announce("Upload failed: %s" % str(e), log.ERROR)      
