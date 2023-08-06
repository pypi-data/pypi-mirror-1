"""
  DrAdm1 utilities pack - www.dradm.org
  2009 (c) Axel <dev@axel.pp.ru>
  Under GPL v3
"""

import optparse, signal
from mod import changelog, database, dbuser
from mod.utils import *

def main():
    """ Add database to the project.
    """
    if not rootcheck():
        errexit("You need superuser privileges!")
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        config = Config()
        config.security()
    except (UtilityError, ConfigError), err:
        errexit(err.msg)
    cli = optparse.OptionParser(description="Setup database for the project. Part of DrAdm1 utilities pack. http://dradm.org",
                                version="1.0", usage="%prog [options] <site> <database>")
    cli.add_option("--verbose", "-v", help="verbose output to the console",
                   action="store_true", default=False)
    cli.add_option("--user", "-U", help="setup alternative username",
                   default=False)
    cli.add_option("--password", "-P", help="setup password instead of password autogeneration",
                   default=False)    
    cli.add_option("--database", "-D", help="setup alternative database name",
                   default=False)
    cli.add_option("--project", "-p", help="select project for this virtual host",
                   type="string", default="")
    cli.add_option("--type", "-t", help="type of the DBMS, one of: MYSQL (default), POSTGRES",
                   dest="dbtype", type="string", default="MYSQL")
    try:
        chlog = changelog.Changelog(config, cli.get_prog_name())
    except changelog.ChangelogError, err:
        errexit(err.msg)
    opt, arg = cli.parse_args()
    if not arg:
        chlog.host_news()
        print "Type -h for command help."
        exit()
    databasename = sanity(arg[0], 32)
    if opt.user:
        username = sanity(opt.user, 16)
    elif opt.project:
        username = sanity(opt.project, 16)
        chlog.project_set(opt.project)
    else:
        username = sanity(databasename, 16)
    try:
        db = database.Database(config, databasename, opt.project, opt.dbtype)
        if db.exists():
            errexit("Database %s already exists!" % db.getname())
        db.add()
        print "* Database: %s" % db.getname()
        chlog.add("Database %s created." % db.getname())
        if opt.verbose:
            print "Database %s created OK." % db.getname()
        user = dbuser.DbUser(config, username, opt.project, opt.dbtype)
        if not user.exists():
            user.add(opt.password)
            print "* User: %s" % user.getname()
            print "* Passwd: %s" % user.getpasswd()
            if opt.verbose:
                print "New user created OK."
        user.grant(db.getname())
        chlog.add("Database user %s created." % user.getname())
        if opt.verbose:
            print "User %s got access to %s database." % (user.getname(), db.getname())
            print "* Connect string: mysql://%s:%s@%s/%s" % (user.getname(), user.getpasswd(), db.gethost(), db.getname())
    except database.DatabaseError, err:
        errexit(err.msg)
    except dbuser.DbUserError, err:
        errexit(err.msg + " Can't setup database user %s for created database!" % user.getname())
    except ConfigError, err:
        errexit(err.msg)
    except SystemExit:
        pass
    except:
        errexit("Utility internal error.")


if __name__ == "__main__":
    main()
