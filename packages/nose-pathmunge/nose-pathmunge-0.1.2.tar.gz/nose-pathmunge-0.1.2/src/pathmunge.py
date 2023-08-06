"""
Simple nose plugin to allow a user to chain additional directories onto
their pythonpath.
"""

from nose.plugins.base import Plugin
import os
import sys

class PathMunge(Plugin):

    enabled = False
    name = "pathmunge"
    score = 3
    env_opt = "NOSE_ADDITIONAL_PATHS"
    def options(self, parser, env=os.environ):
        """ Define the command line options for the plugin. """
        parser.add_option(
            "--with-path", action="append",
            dest="additional_paths",
            help="Additional directories to add to the nose sys.path [NOSE_ADDITIONAL_PATHS]")

    def configure(self, options, noseconfig):
        """ Call the super and then validate and call the relevant parser for
        the configuration file passed in """
        if not options.additional_paths:
            self.enabled = False
            return
        Plugin.configure(self, options, noseconfig)

        all_paths = []
        for path in options.additional_paths:
            if len(path.split(',')) > 1:
                all_paths.extend(path.split(','))
            else:
                all_paths.append(path)
        for path in all_paths:
            path = os.path.expanduser(path)
            path = os.path.abspath(path)
            if not os.path.isdir(path):
                raise Exception('%s is not a directory' % path)
        sys.path.extend([path for path in all_paths])
