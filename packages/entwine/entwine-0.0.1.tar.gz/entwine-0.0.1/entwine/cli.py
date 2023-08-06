"""

cli.py
======

Desc: Command-line tool for querying twine.com

Author: Rob Cakebread <cakebread a t gmail.com>

License : New BSD (See COPYING)

"""

__docformat__ = 'restructuredtext'
__revision__ = '$Revision: 180 $'[11:-1].strip()


import sys
import optparse
import logging
import urllib2

from entwine.entwinelib import get_profile
#from entwine.plugins import load_plugins
from entwine.__init__ import __version__ as VERSION



class Entwine(object):

    """
    Main class for entwine
    """

    def __init__(self):
        self.options = None
        self.logger = logging.getLogger("entwine")


    #def get_plugin(self, method):
    #    """
    #    Return plugin object if CLI option is activated and method exists

    #    @param method: name of plugin's method we're calling
    #    @type method: string

    #    @returns: list of plugins with `method`

    #    """
    #    all_plugins = []
    #    for entry_point in pkg_resources.iter_entry_points('entwine.plugins'):
    #        plugin_obj = entry_point.load()
    #        plugin = plugin_obj()
    #        plugin.configure(self.options, None)
    #        if plugin.enabled:
    #            if not hasattr(plugin, method):
    #                self.logger.warn("Error: plugin has no method: %s" \
    #                       % method)
    #                plugin = None
    #            else:
    #                all_plugins.append(plugin)
    #    return all_plugins

    def set_log_level(self):
        """
        Set log level according to command-line options

        @returns: logger object
        """

        if self.options.debug:
            self.logger.setLevel(logging.DEBUG)
        elif self.options.quiet:
            self.logger.setLevel(logging.ERROR)
        else:
            self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        return self.logger

    def run(self):
        """
        Perform actions based on CLI options
        
        @returns: status code
        """
        opt_parser = setup_opt_parser()
        (self.options, remaining_args) = opt_parser.parse_args()
        self.set_log_level()

        if len(sys.argv) == 1 or len(remaining_args) > 2:
            opt_parser.print_help()
            return 2

        commands = ['profile', 'entwine_version']

        #Run first command it finds, and only the first command, then return
        for action in commands:
            if getattr(self.options, action):
                return getattr(self, action)()
        opt_parser.print_help()

    def profile(self):
        """Print a user's profile to stdout"""
        username = sys.argv[2]
        try:
            self.logger.info(get_profile(username))
        except urllib2.HTTPError:
            self.logger.error("Profile for user %s not found." % username)
            

    def entwine_version(self):
        """
        Show entwine's version

        @returns: 0
        """
        self.logger.info("entwine version %s (rev. %s)" % \
                (VERSION, __revision__))
        return 0


def setup_opt_parser():
    """
    Setup the optparser

    @returns: opt_parser.OptionParser
    
    """

    usage = "usage: %prog [options]"
    opt_parser = optparse.OptionParser(usage=usage)

    opt_parser.add_option("--version", action='store_true', dest=
                          "entwine_version", default=False, help=
                          "Show entwine version and exit.")

    opt_parser.add_option("--debug", action='store_true', dest=
                          "debug", default=False, help=
                          "Show debugging information.")

    opt_parser.add_option("-q", "--quiet", action='store_true', dest=
                          "quiet", default=False, help=
                          "Show less output.")

    opt_parser.add_option("-p", "--profile", action='store', dest=
                          "profile", default=False, help=
                          "Show user's information.")

    ## add opts from plugins
    #all_plugins = []
    #for plugcls in load_plugins(others=True):
    #    plug = plugcls()
    #    try:
    #        plug.add_options(opt_parser)
    #    except AttributeError:
    #        pass

    return opt_parser


def main():
    """
    Let's do it.
    """
    my_entwine = Entwine()
    my_entwine.run()

if __name__ == "__main__":
    sys.exit(main())

