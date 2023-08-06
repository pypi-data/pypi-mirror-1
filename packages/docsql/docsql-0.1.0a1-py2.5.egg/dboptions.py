#!/usr/bin/env python
from __future__ import division

__version__ = "$Revision: 1.4 $"

"""
leaves you with annoying dictionary entries called "dboptions.db" with
None in options as well as the dict in dboptions

usage:

parser = OptionParser()
dboptions.add_to_parser(parser)
"""

import sys

from optparse import Option, OptionGroup, OptionParser, Values

GROUP_CAPTION = "Database options"

# XXX: the DictOption stuff is madness and unnecessary
# just call the options _dboptions_xxx and deal with it in connect()
class DictOptionParser(OptionParser):
    def get_default_values(self):
        if not self.process_default_values:
            # Old, pre-Optik 1.5 behaviour.
            return Values(self.defaults)

        defaults = self.defaults.copy()
        for option in self._get_all_options():
            default = defaults.get(option.dest)
            if isinstance(default, basestring):
                opt_str = option.get_opt_string()
                dest = option.dest
                value = option.check_value(opt_str, default)

                try:
                    dict_name, key = dest.split(".")
                    defaults.setdefault(dict_name, {})[key] = value
                except ValueError:
                    defaults[dest] =  value

        return Values(defaults)

class DictOption(Option):
    _EXTRA_ACTION = ("store_dict",)
    ACTIONS = Option.TYPES + _EXTRA_ACTION
    STORE_ACTIONS = Option.STORE_ACTIONS + _EXTRA_ACTION
    TYPED_ACTIONS = Option.TYPED_ACTIONS + _EXTRA_ACTION

    def __init__(self, *args, **keywds):
        Option.__init__(self, *args, **keywds)

        if "action" not in keywds:
            self.action = "store_dict"

    def take_action(self, action, dest, opt, value, values, parser):
        dict_name, key = self.dest.split(".")
        if action == "store_dict":
            values.ensure_value(dict_name, {})[key] = value
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)

OPTIONS = [DictOption("-d", "--driver", dest="dboptions.driver",
                      default="MySQLdb",
                      metavar="DRIVER", help="use driver DRIVER"),
           DictOption("-D", "--database", dest="dboptions.db",
                      metavar="DATABASE", help="use database DATABASE"),
           DictOption("-h", "--host", dest="dboptions.host",
                      metavar="HOST", help="connect to host HOST"),
           DictOption("-p", "--password", dest="dboptions.passwd",
                      metavar="PASSWORD", help="login with password PASSWORD"),
           DictOption("-P", "--port", dest="dboptions.port", type=int,
                      metavar="PORT", help="use port PORT"),
           DictOption("-u", "--user", dest="dboptions.user",
                      metavar="USER", help="login with user USER")]

def add_to_parser(parser):
    old_conflict_handler = parser.conflict_handler
    parser.set_conflict_handler("resolve")

    try:
        group = OptionGroup(parser, GROUP_CAPTION)

        for option in OPTIONS:
            group.add_option(option)

        parser.add_option_group(group)
    finally:
        parser.set_conflict_handler(old_conflict_handler)

class DbOptionParser(DictOptionParser):
    def __init__(self, *args, **kwargs):
        DictOptionParser.__init__(self, *args, **kwargs)
        add_to_parser(self)

def connect(dboptions):
    dboptions_copy = dboptions.copy()
    del dboptions_copy["driver"]

    driver = __import__(dboptions["driver"])
    return driver.connect(**dboptions_copy)

def main(args):
    pass

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
