#!python
"""Setuptools-based installation and packaging module"""

# Ensure setuptools is available (download & install if necessary)
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

# Get package information (and googlecode_upload Command class)
import os
execfile(os.path.join("brainfreeze", "release", "__init__.py"))

# Check to make sure required python is available
def check_python():
    if sys.version_info < (2,3):
        print "Python 2.3 or higher is required to run BrainFreeze."
        sys.exit(1)

# Load long description from README file
readme = os.path.normpath(__file__ + "/../README")
f = open(readme)
LONG_DESCRIPTION = f.read()

# Let setuptools work its magic!
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
	packages=find_packages(), # find python packages in this dir
	include_package_data=True, # include more than just the code
	cmdclass={'googlecode_upload': googlecode_upload},
	keywords=["brainfreeze", "sqlalchemy", "orm"],
    test_suite="brainfreeze.test.test_docs.test_suite",
    classifiers=[
        "Development Status :: 3 - Alpha",
    #     "Environment :: Console",
    #     "Environment :: Plugins",
         "Intended Audience :: Developers",
    #     "Intended Audience :: End Users/Desktop",
         "License :: OSI Approved :: BSD License",
         "Operating System :: OS Independent",
         "Programming Language :: Python",
         "Topic :: Software Development :: Libraries :: Python Modules",
    #     "Topic :: Software Development :: Version Control",
    #     "Topic :: System :: Archiving",
    #     "Topic :: Utilities"
    ],
)


