"""
  DrAdm1 utilities pack - www.dradm.org
  2009 (c) Axel <dev@axel.pp.ru>
  Under GPL v3
"""

import optparse, signal
from mod import changelog, utils
from mod.utils import *

def main():
    """ Browse changelog or add new record to it.
    """
    if not rootcheck():
        errexit("You need superuser privileges!")
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        config = Config()
        config.security()
    except (UtilityError, ConfigError), err:
        errexit(err.msg)
    cli = optparse.OptionParser(description="Browse and edit host changelog. Part of DrAdm1 utilities pack. http://dradm.org",
                                version="1.0", usage="%prog [options] [filter_str]")
    cli.add_option("--verbose", "-v", help="verbose output to the console",
                   action="store_true", default=False)
    cli.add_option("--add", "-a", help="add message to the changelog",
                   default='')
    cli.add_option("--project", "-p", help="changes related to project",
                   type="string", default="")
    cli.add_option("--utility", "-u", help="filter changes related to specified utility",
                   type="string", default="")
    opt, arg = cli.parse_args()
    try:
        log = changelog.Changelog(config, cli.get_prog_name(), sanity(opt.project))
        if opt.add:
            log.add(opt.add)
            if opt.verbose:                
                print "Record added to changelog OK."
        elif not arg:
            log.log_print()
        else:
            log.log_print(arg[0])
    except changelog.ChangelogError, err:
        errexit(err.msg)
    except ConfigError, err:
        errexit(err.msg)
    except SystemExit:
        pass
    except:
        errexit("Utility internal error.")


if __name__ == "__main__":
    main()
