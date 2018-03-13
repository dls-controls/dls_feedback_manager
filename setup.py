from setuptools import setup

# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")

setup(
#    install_requires = ['cothread'], # require statements go here
    name = 'dls_feedback_manager',
    version = version,
    description = 'Module',
    author = 'sfx44126',
    author_email = 'sfx44126@fed.cclrc.ac.uk',
    packages = ['dls_feedback_manager'],
#    entry_points = {'console_scripts': ['test-python-hello-world = dls_feedback_manager.dls_feedback_manager:main']}, # this makes a script
#    include_package_data = True, # use this to include non python files
    zip_safe = False
    )
