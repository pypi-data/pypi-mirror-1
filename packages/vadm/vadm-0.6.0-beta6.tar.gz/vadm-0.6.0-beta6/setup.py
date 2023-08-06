
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    extra = {}
    PACKAGES = ['vadm', 'vadm.test', 'vadm.doc']
else:    
    extra = dict(install_requires = ['py==1.0.2'],)
    PACKAGES = find_packages()

setup(name = "vadm",
    version = "0.6.0-beta6", 
    description = "tool for versioning system files and directories",
    author = "holger krekel, merlinux GmbH", 
    author_email = "holger@merlinux.de",
    license = "GPL V2 or later",
    scripts = ['vadm/bin/vadm'],
    packages = PACKAGES,
    long_description = ("vadm is a simple svn-like command line tool "
                        "for versioning unix system files including "
                        "tracking of POSIX ownership and permission "
                        "information."),
    url = "http://codespeak.net/vadm",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)", 
        "Operating System :: POSIX", 
        "Programming Language :: Python",
        "Topic :: System :: Systems Administration",
    ],
    **extra
    )
