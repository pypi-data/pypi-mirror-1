from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name = "MyghtyUtils",
    version = "0.51",
    description = "Container and Utility Functions from the Myghty Template Framework",
    author = "Mike Bayer",
    author_email = "mike@myghty.org",
    url = "http://www.myghty.org",
    package_dir = {'':'lib'},
    packages = find_packages('lib'),
    license = "MIT License",
    long_description = """\
This is the set of utility classes used by Myghty templating.  Included are:

container - the Containment system providing back-end neutral key/value storage, 
with support for in-memory, DBM files, flat files, and memcached

buffer - some functions for augmenting file objects

util - various utility functions and objects

synchronizer - provides many reader/single writer synchronization using 
either thread mutexes or lockfiles

session - provides a Session interface built upon the Container, similar 
interface to mod_python session.  Currently needs a mod_python-like request object,
this should be changed to something more generic.
`Development SVN <http://svn.myghty.org/myghtyutils/trunk#egg=myghtyutils-dev>`_

""",
    classifiers = ["Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    ],
    )


