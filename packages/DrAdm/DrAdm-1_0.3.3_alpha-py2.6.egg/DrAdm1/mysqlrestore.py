"""
 DrAdm1 utilities pack - www.dradm.org
 2009 (c) Axel <dev@axel.pp.ru>
 Under GPL v3
"""

import datetime, optparse, signal
from mod import backup, changelog
from mod.utils import *
    

def main():
    """ Restore MySQL database from backup.
    """
    if not rootcheck():
        errexit("You need superuser privileges!")
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        config = Config()
        config.security()
    except (UtilityError, ConfigError), err:
        errexit(err.msg)
    cli = optparse.OptionParser(description="Restore MySQL database from backup. Part of DrAdm1 utilities pack. http://dradm.org", version=VERSION, usage="%prog [options] <database_name>")
    cli.add_option("--date", "-d", help="find backup for the selected date (set date as YY-MM-DD), instead mostly fresh backup will used",
                   default=False)
    cli.add_option("--no-data", "-n", help="import only structures with no data",
                   action="store_true", default=False)
    cli.add_option("--database", "-D", help="import into alternative database",
                   default=False)    
    cli.add_option("--list", "-l", help="list backup files for the selected database and/or date",
                   action="store_true", default=False)
    cli.add_option("--yes", "-y", help="automatically answer YES on all questions asked by the program",
                   action="store_true", default=False)
    cli.add_option("--verbose", "-v", help="verbose output to the console",
                   action="store_true", default=False)
    try:
        chlog = changelog.Changelog(config, cli.get_prog_name())
    except changelog.ChangelogError, err:
        errexit(err.msg)
    opt, arg = cli.parse_args()
    if arg:
        dbname = arg[0]
    elif not opt.list:
        print chlog.host_news()
        errexit("You need to select one database.")
    else:
        dbname = '*'
    if opt.database:
        dest_dbname = sanity(opt.database)
    else:
        dest_dbname = dbname
    if opt.date:
        try:
            date = datetime.datetime.strptime(opt.date, '%Y-%m-%d')
        except:
            try:
                date = datetime.datetime.strptime(opt.date, '%y-%m-%d')
            except:
                errexit("Bad date.")
        date = datetime.date(date.year, date.month, date.day).isoformat()
    else:
        date = '*'
    try:
        mysql = backup.MysqlBackup(config, dbname, date, verbose=opt.verbose)
        chlog = changelog.Changelog(config, cli.get_prog_name())
        question = ("Current data of %s database will lost! Are you really want to overwrite current database %s with data from backup?" % (dest_dbname, dest_dbname)).upper()
        if opt.list:
            mysql.list_print()
        elif opt.yes or not opt.yes and confirmed(question):
            mysql.restore(with_data=not opt.no_data, destdb=dest_dbname)
            chlog.add("Database %s restored from backup with name %s" % (dbname, dest_dbname))
            if opt.verbose:
                print "Database %s restored OK." % dest_dbname
        else:
            okexit("Operation cancelled. Database untouched.")
    except backup.BackupError, err:
        errexit(err.msg)
    except ConfigError, err:
        errexit(err.msg)
    except SystemExit:
        pass
    except:
        errexit("Utility internal error.")

        

if __name__ == "__main__":
    main()
    
