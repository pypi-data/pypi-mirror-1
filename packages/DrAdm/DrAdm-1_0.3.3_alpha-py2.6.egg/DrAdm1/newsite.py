"""
 DrAdm1 utilities pack - www.dradm.org
 2009 (c) Axel <dev@axel.pp.ru>
 Under GPL v3
"""

import optparse, signal
from mod import database, dbuser, vhost
from mod.utils import *

def main():
    """ Add virtual host, users and appropriate database.
    """
    if not rootcheck():
        errexit("You need superuser privileges!")
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        config = Config()
        config.security()
    except (UtilityError, ConfigError), err:
        errexit(err.msg)
    cli = optparse.OptionParser(description="Setup virtual host. Part of DrAdm1 utilities pack. http://dradm.org", version="1.0", usage="%prog [options] <sitename>")
    cli.add_option("--verbose", "-v", help="increase verbosity of this program",
                   action="store_true", default=False)
    cli.add_option("--force", "-f", help="overwrite existing virtual host config and files if it exists",
                   action="store_true", default=False)
    cli.add_option("--no-database", "-d", help="setup virtual host without database",
                   action="store_true", default=False)
    cli.add_option("--project", "-p", help="select project for this virtual host",
                   type="string", default="")
    # Drupal parameters moved to separated `drupal` utility
    #    cli.add_option("--type", "-t", help="type of the DBMS, one of: MYSQL (default), POSTGRES",
    #                   dest="dbtype", type="string", default="mysql")    
    opt, arg = cli.parse_args()
    if not arg:
        cli.print_help()
        exit()
    name = sanity(arg[0])
    sitename = arg[0].lower()
    try:
        apache = vhost.ApacheVhost(config, sitename, opt.project)
        db = database.Database(config, name, opt.project)
        db_user = dbuser.DbUser(config, name, opt.project)
        #if opt.dbtype == "drupal":
        #    drupal_files = drupal.DrupalHost(config, name, opt.project)            
        try:
            if not (opt.force and apache.exists()):
                apache.add()
        except:
            apache.drop()
            raise
        #try:            
        #    if opt.dbtype == "drupal":
        #        drupal_files.add()
        #except:
        #    drupal_files.drop()
        #    raise
        try:
            db.add()
        except:
            db.drop()
            raise
        try:
            db_user.add()
            print "* User: %s" % db_user.getname()
            print "* Passwd: %s" % db_user.getpasswd()
            created_ok = True
            if opt.verbose:
                print "New user %s created OK." % db_user.getname()
                created_ok = True
            db_user.grant(db.getname())
            if opt.verbose:
                print "User %s got access to %s database." % (db_user.getname(), db.getname())
                if created_ok:
                    print "* Connect string: mysql://%s:%s@%s/%s" % (db_user.getname(), db_user.getpasswd(), db_user.getserverhost(), db.getname())
        except:
            db_user.drop()
            raise
    except vhost.VhostError, err:
        errexit(err.msg)
    except database.DatabaseError, err:
        errexit(err.msg)
    except dbuser.DbUserError, err:
        errexit(err.msg + " Can't setup database user %s for created database!" % db_user.getname())
    except ConfigError, err:
        errexit(err.msg)
    except SystemExit:
        pass
    except:
        errexit("Utility internal error.")
    if opt.verbose:
        print "Virtual host %s created." % sitename


if __name__ == "__main__":
    main()
