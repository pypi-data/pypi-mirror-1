
"""

utils.py
===========

Misc helper funcitions 
----------------------

Author: Rob Cakebread <cakebread@ gmail. com>

License  : New BSD (See COPYING)




"""

__docformat__ = 'restructuredtext'

import os
from configobj import ConfigObj


def get_user_passwd():
    """Return a tuple of (username, password)"""
    get_rcfile_path()
    config = ConfigObj(get_rcfile_path())
    return config['username'], config['password']

def get_entwine_dir():
    """Return path where we store config files and data"""
    twinedir = os.path.abspath(os.path.expanduser("~/.entwine"))
    if not os.path.exists(twinedir):
        os.mkdir(twinedir)
        template = """username = "twine_username"\npassword = "twine_password"
        """
        open("%s/entwinerc" % twinedir, "w").write(template)
    return twinedir

def get_rcfile_path():
    """Return path of rc config file"""
    return os.path.abspath("%s/entwinerc" % get_entwine_dir())

