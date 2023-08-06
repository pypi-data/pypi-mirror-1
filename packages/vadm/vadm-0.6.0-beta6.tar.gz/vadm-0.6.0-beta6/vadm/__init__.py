# Copyright 2008, Holger Krekel. Licensed under GPL V3.
"""\
vadm is a simple svn-like command line tool tool for 
freely versioning unix system files and directories including 
tracking of POSIX ownership and permission information.  
"""  
from py import initpkg 

initpkg(__name__, 
    description = "tool for versioning system files and directories",
    revision = '$LastChangedRevision: 11405 $',
    lastchangedate = '$LastChangedDate: 2005-04-24 15:18:48 +0200 (Sun, 24 Apr 2005) $',
    version = "0.6.0-beta5", 
    url = "http://codespeak.net/vadm",
    #download_url = "http://codespeak.net/download/py/py-0.6.0-pre-alpha.tar.gz", 
    license = "GPL V3",
    platforms = ['unix', 'linux'], 
    author = "holger krekel, merlinux GmbH", 
    author_email = "holger@merlinux.de",
    long_description = globals()['__doc__'],

    exportdefs = {
        'cmdline.main'         : ('./cmdline.py', 'main'), 
        'sync.update_hostwc'   : ('./sync.py', 'update_hostwc'), 
        'sync.all_fs2wc'       : ('./sync.py', 'all_fs2wc'), 
        'sync.posix_fs2wc'     : ('./sync.py', 'posix_fs2wc'), 
        'sync.content_fs2wc'   : ('./sync.py', 'content_fs2wc'), 
        'sync.wc2fs'           : ('./sync.py', 'wc2fs'), 
        'sync.getposix'        : ('./sync.py', 'getposix'), 
        'sync.vadmpropname'    : ('./sync.py', 'vadmpropname'), 
        'sync2.FileServer': ('./sync2.py', 'FileServer'), 
    }
)
