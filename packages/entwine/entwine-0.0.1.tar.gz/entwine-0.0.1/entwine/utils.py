
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

    config = ConfigObj(get_rcfile_path())
    return config['username'], config['password']

def get_entwine_dir():
    """Return path where we store config files and data"""

    return os.path.abspath("%s/.twine" % os.path.expanduser("~"))

def get_rcfile_path():
    """Return path of rc config file"""

    return os.path.abspath("%s/twinerc" % get_entwine_dir())

