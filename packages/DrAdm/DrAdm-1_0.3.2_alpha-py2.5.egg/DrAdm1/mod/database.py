"""
 DrAdm1 utilities pack - www.dradm.org
 (c) Axel <dev@axel.pp.ru>
 Under GPL v3
"""

from utils import *


class DatabaseError(Exception):
    def __init__(self, obj, msg=''):
        self.type = obj.section
        self.name = obj.name
        self.project = obj.project
        self.msg = msg
        if not self.msg:
            self.msg = "Operation error in 'database' module."

    def __str__(self):
        return self.msg


class MySQLDatabase:
    """ Methods for MySQL database.
    """
    def __init__(self, config, name, project):
        try:
            import MySQLdb as DB
        except DeprecationWarning:
            pass
        except:
            DatabaseError(self, "MySQL support not installed. You need install python-mysql module to the system.")
        self.DB = DB
        self.section = 'MYSQL'
        self.name = name
        self.project = project
        if self.project:
            self.realname = "%s_%s" % (self.project, self.name)
        else:
            self.realname = self.name
        self.host = config.get(self.section, 'host')
        user = config.get(self.section, 'user')
        passwd = config.get(self.section, 'passwd')
        try:
            db = self.DB.connect(host = self.host, user = user, passwd = passwd)
            self.cursor = db.cursor()
        except:
            raise DatabaseError(self, "Can't connect to MySQL server at %s" % self.host)

    def getname(self):
        """ Return name of the created database.
        """
        return self.realname

    def gethost(self):
        """ Return hostname of the database server as it defined in the config.
        """
        return self.host
    
    def exists(self):
        """ Check is database exists?
        """
        try:
            return self.cursor.execute("SHOW DATABASES LIKE %s", self.realname)
        except:
            raise DatabaseError(self, "Can't determinate availability of the database %s" % self.realname)

    def add(self):
        """ Create new database.
        """
        try:
            # TODO move charset and collate options to config!
            self.cursor.execute("CREATE DATABASE %s CHARACTER SET utf8 COLLATE utf8_unicode_ci" % self.realname)
        except self.DB.ProgrammingError:
            raise DatabaseError(self, "Can't create database %s" % self.realname)

    def drop(self):
        """ Delete database structure and data.
        """
        try:
            self.cursor.execute('DROP DATABASE %s' % self.realname)
        except self.DB.ProgrammingError:
            raise DatabaseError(self, "Can't delete database %" % self.realname)


class PostgresDatabase:
    def __init__(self, config, name, project):
        import pgdb as DB
        self.DB = DB
        self.section = 'POSTGRES'
        self.name = name
        self.project = project
        if self.project:
            self.realname = "%s_%s" % (self.project, self.name)
        else:
            self.realname = self.name
        host = config.get(self.section, 'host')
        user = config.get(self.section, 'user')
        passwd = config.get(self.section, 'passwd')
        try:
            db = self.DB.connect(host = host, user = user, passwd = passwd)
            self.cursor = db.cursor()
        except:
            raise DatabaseError(self, "Can't connect to MySQL server at %s" % host)


class Database:
    """ Work with databases. Wrap around Mysql and Postgres classes.
    """
    def __init__(self, config, name, project='', dbtype='MYSQL'):
        self.section = dbtype.upper()
        self.name = name
        self.project = project
        if not self.section or self.section == 'MYSQL':
            self.server = MySQLDatabase(config, self.name, self.project)
        elif self.section == 'POSTGRES' or self.section == 'POSTGRE':
            self.server = PostgresDatabase(config, self.name, self.project)
        else:
            raise DatabaseError(self, "The %s database server don't supported." % dbtype.upper())

    def getname(self):
        """ Returns database name used really used in RDBMS.
        """
        return self.server.getname()

    def gethost(self):
        """ Return hostname of the database server as it defined in the config.
        """
        return self.server.gethost()
    
    def exists(self):
        """ Check is database exists?
        """
        return self.server.exists()
    
    @addactions
    def add(self):
        """ Create new database.
        """
        self.passwd = self.server.add()

    @addactions
    def drop(self):
        """ Delete database structure and data.
        """
        self.server.drop()


if __name__ == '__main__':
    """ Quick unit test
    """
    if not rootcheck():
        error("You need run this utility as root!")
    config = Config()
    test = Database(config, 'testdb')
    if test.add():
        print "Created OK"
    if test.drop():
        print "Dropped OK"

