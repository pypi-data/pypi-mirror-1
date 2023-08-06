"""
  DrAdm1 utilities pack - www.dradm.org
  2009 (c) Axel <dev@axel.pp.ru>
  Under GPL v3
"""

import optparse, signal
from mod import utils, dbuser
from mod.utils import *

def main():
    """ Add user to DBMS. Also set permissions for this user on the selected database.
    """
    if not rootcheck():
        errexit("You need superuser privileges!")
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        config = Config()
        config.security()
    except (UtilityError, ConfigError), err:
        errexit(err.msg)
    cli = optparse.OptionParser(description="Create new database user. Part of DrAdm1 utilities pack. http://dradm.org",
                                version="1.0", usage="%prog [options] <user[@host_or_ip]> [database]")
    cli.add_option("--verbose", "-v", help="verbose output to the console",
                   action="store_true", default=False)
    cli.add_option("--project", "-p", help="select project for this virtual host",
                   type="string", default="")
    cli.add_option("--type", "-t", help="type of the DBMS, one of: MYSQL (default), POSTGRES",
                   dest="dbtype", type="string", default="MYSQL")
    opt, arg = cli.parse_args()
    if not arg:
        cli.print_help()
        exit()
    try:
        if arg[0].find('@'):
            uname, host = arg[0].split('@')
            host = sanity_host(host)
        else:
            uname = arg[0]
            host = 'localhost'
        uname = sanity(uname)
        if len(arg) > 1:
            dbname = sanity(arg[1])
        else:
            dbname = ''
        user = dbuser.DbUser(config, uname, opt.project, host, opt.dbtype)
        created_ok = False
        if user.exists():
            if opt.verbose:
                print "User %s already exists." % user.getname()
        else:
            user.add()
            print "* User: %s@%s" % (user.getname(), user.get_clienthost())
            print "* Passwd: %s" % user.getpasswd()
            if opt.verbose:
                print "New user %s created OK." % user.getname()
                created_ok = True
        if dbname:
            user.grant(dbname)
            if opt.verbose:
                print "User %s got access to %s database." % (user.getname(), dbname)
                if created_ok:
                    print "* Connect string: mysql://%s:%s@%s/%s" % (user.getname(), user.getpasswd(), user.get_serverhost(), dbname)
        if opt.verbose and host != 'localhost':
            print "* Connections allowed only from %s" % user.get_clienthost()
    except dbuser.DbUserError, err:
        try:
            user.drop()
            errexit(err.msg + " Can't properly setup database user %s! User was dropped." % user.getname())
        except dbuser.DbUserError, err:
            errexit(err.msg + " Can't properly setup database user %s! And can't drop wrong user! Repair manually... :(" % user.getname())

    except ConfigError, err:
        errexit(err.msg)
    except SystemExit:
        pass
    except:
        errexit("Utility internal error.")


if __name__ == "__main__":
    main()
