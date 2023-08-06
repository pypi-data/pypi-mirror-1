#!/usr/bin/env python

"""
 DrAdm1 utilities pack - www.dradm.org
 2009 (c) Axel <dev@axel.pp.ru>
 Under GPL v3
"""

import os, sys, glob, tarfile, shutil
from subprocess import *
from utils import *


class BackupError(Exception):
    """ Display errors for Backup classes.
    """
    def __init__(self, obj, msg=''):        
        Exception.__init__(self)
        self.type = obj.section
        self.name = obj.name
        self.project = obj.project
        self.msg = msg or "Operation error in 'backup' module."
        
    def __str__(self):
        return self.msg


class MysqlBackup:
    """ Work with MySQL backups (in format of the `mysqlbackup` utility).
    """
    def __init__(self, config, name='*', date='*', project='', verbose=False):
        if name == '*':
            self.name = name
        else:
            self.name = sanity(name)
        self.date = date
        self.project = sanity(project)
        self.files = []
        self.section = 'MYSQL'
        try:
            import MySQLdb
            self.MySQLdb = MySQLdb
        except ImportError:
            raise BackupError(self, "Python installed without MySQL support. You need to install python mysql package.")
        self.tmp = config.get('COMMON', 'tmp')  
        self.mysql_pass = config.get(self.section, 'passwd')
        self.mysql_host = config.get(self.section, 'host')
        self.mysql_user = config.get(self.section, 'user')
        self.section = 'BACKUP'
        self.mysql_path = config.get(self.section, 'mysql_path')
        self.mysql_file = config.get(self.section, 'mysql_file')
        self.arc = config.get(self.section, 'arc')
        self.verbose = verbose

    def _files(self, date):
        variables = {'DBNAME': self.name, 'DATE': date}
        fname = self.mysql_file % variables
        if self.arc == 'gzip':
            fname += '.tar.gz'
        elif self.arc == 'bzip2':
            fname += '.tar.bz2'
        self.files = glob.glob(os.path.join(self.mysql_path, fname))
        self.files.sort(reverse=True)
        if not self.files:
            raise BackupError(self, "Backup files not found. May be you used full path for database name?")

    def backup(self):
        """ Backup database <name> or backup all databases.
        """
        try:
            return call(['mysqlbackup', '%s' % self.name])
        except:
            raise BackupError(self, "Error running `mysqlbackup` external utility.")

    def list_get(self):
        """Get backups list
        """
        self._files(self.date)
        return self.files
    
    def list_print(self):
        """ Print all backups for selected database or backups for all databases
        """
        self._files(self.date)
        self.files.sort()
        for f in self.files:
            print os.path.basename(f)

    @addactions
    def restore(self, with_data=True, destdb=''):
        """ Restore database. Current database will copied to safe place before overwriten from backup.
        """
        if not destdb:
            destdb = self.name  # by default we restore data to same database
        destdb = destdb.lower()
        if destdb == "information_schema":  # denied access to MySQL information schema, we can backup it, but not restore with dradm
            raise BackupError(self, "Can't restore MySQL service database 'information_schema' due security restrictions!")
        self._files(self.date)
        fname = self.files[0]
        try:
            db = self.MySQLdb.connect(host = self.mysql_host, user = self.mysql_user, passwd = self.mysql_pass)
        except self.MySQLdb.OperationalError:
            raise BackupError(self, "Database connect problem: %s" % sys.exc_info()[1])
        cursor = db.cursor()
        ## Unpack files
        try:
            os.chdir(self.tmp)
        except:
            error("Can't create or change temporary directory to %s" % self.tmp);
        arc = tarfile.open(fname, 'r')
        arc.extractall()
        ## Dump old database (run mysqlbackup)
        # TODO must self.backup() to another name!

        ## Prepare database
        try:
            cursor.execute('DROP DATABASE IF EXISTS %s' % destdb)
        except:
            pass
        cursor.execute('CREATE DATABASE %s' % destdb)
        cursor.execute('USE %s' % destdb)
        cursor.execute('SET FOREIGN_KEY_CHECKS = 0')  # only InnoDB affected, but only InnoDB now support constraints
        # for info: http://dev.mysql.com/doc/refman/5.1/en/innodb-foreign-key-constraints.html
        if self.verbose:
            print "Database %s recreated OK." % destdb
        ## Load sql
        for filename in filter(lambda x: x[-4:] == '.sql', arc.getnames()):
            sql = open(filename, 'r')
            mysql = Popen('mysql -u %s -p%s -h %s -D %s' % (self.mysql_user, self.mysql_pass, self.mysql_host, destdb),
                          shell=True, stdin=sql, stdout=PIPE, stderr=PIPE)
            mysql.wait()  # TODO change to poll()
        if self.verbose:
            print "Structures recreated OK."
        ## Load data
        if self.verbose:
            stdout = False
            print "Loading data..."
        else:
            stdout = open('/dev/null')
        if with_data:
            for filename in filter(lambda x: x[-4:] == '.txt', arc.getnames()):
                call(['mysqlimport', '-u%s' % self.mysql_user, '-p%s' % self.mysql_pass, '-L', '%s' % destdb, '%s' % filename],
                     stdout=stdout)
        cursor.execute('SET FOREIGN_KEY_CHECKS = 1') # set constraints ON
        # Drop temporary files
        try:
            shutil.rmtree(os.path.join(self.tmp, self.name))
        except:
            raise BackupError(self, "Restored OK, but can't delete temporary files. Delete manually directory %s." % os.path.join(self.tmp, self.name))


class DatabaseBackup:
    pass


class FileBackup:
    """ Work with file backups.
    TODO complete this class.
    """
    def __init__(self, config):
        self.section = 'Backup'
        self.files_path = config.get(self.section, 'files_path')


class Backup:
    """ Common backup class.
    TODO complete this class.
    """
    def __init__(self, config):
        pass

    def backup(self):
        pass

    def restore(self):
        pass


if __name__ == "__main__":
    """ Quick unit test
    """
    if not rootcheck():
        error("You need run this utility as root!")
    cfg = Config()
    test = MysqlBackup(cfg, 'd6_test')
    print test.backup()
    print test.list_get()
    print test.restore()
