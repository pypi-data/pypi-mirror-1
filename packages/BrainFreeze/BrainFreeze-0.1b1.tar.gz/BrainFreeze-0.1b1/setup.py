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

# Implement a Setuptools Command to generate documentation
class makedocs(Command):
    """Setuptools Command to generate html and wiki documentation"""
    description = "generate BrainFreeze documentation"
    
    user_options = []
    
    def initialize_options(self):
        pass
        
    def finalize_options(self):
        pass

    def run(self):
        # Locate the doc/src directory relative to the current file.
        main_dir = os.path.dirname(os.path.abspath(__file__))
        doc_dir = os.path.join(main_dir, 'brainfreeze', 'doc', 'src')
        wiki_dir = os.path.join(os.path.dirname(main_dir), 'wiki')
        # Walk the doc/src tree and locate all the .txt files
        doc_files = []
        for root, dirs, files in os.walk(doc_dir):
            for name in files:
                if name.endswith('.txt'):
                    path = os.path.join(root, name)
                    doc_files.append(path)
        # Write all the .wiki files!
        from brainfreeze.doc.build import rst2wiki
        for path in doc_files:
            f = open(path)
            source = f.read()
            f.close()
            output = rst2wiki.publish_string(
                source, writer=rst2wiki.WikiWriter()
            )
            wiki_name = os.path.basename(path)[:-len('.txt')] + '.wiki'
            wiki_path = os.path.join(wiki_dir, wiki_name)
            wiki_file = open(wiki_path, 'w')
            wiki_file.write(output)

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
	cmdclass={
	    'googlecode_upload': googlecode_upload,
	    'makedocs': makedocs 
	},
	keywords=["brainfreeze", "sqlalchemy", "orm"],
    test_suite="brainfreeze.test.test_docs.test_suite",
    classifiers=[
         "Intended Audience :: Developers",
         "License :: OSI Approved :: BSD License",
         "Operating System :: OS Independent",
         "Programming Language :: Python",
         "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)


