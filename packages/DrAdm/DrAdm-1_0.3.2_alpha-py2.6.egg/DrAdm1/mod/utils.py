#!/usr/bin/env python

# DrAdm1 utilities pack - www.dradm.org
# 2009 (c) Axel <dev@axel.pp.ru>
# Under GPL v3

VERSION = "1-0.3-rc1-alpha"

import os, string, sys, ConfigParser
from random import choice

__all__ = ['addactions', 'error', 'errexit', 'confirmed', 'okexit', 'rootcheck', 'pwgen', 'sanity', 'sanity_host', 'tail', 'ConfigError', 'UtilityError', 'Config', 'VERSION',]

class UtilityError(Exception):
    """ Display errors for utils.
    """
    def __init__(self, msg=''):        
        Exception.__init__(self)
        self.msg = msg or "Operation error in 'utils' module."
        
    def __str__(self):
        return self.msg


class ConfigError(Exception):
    def __init__(self, name, section):
        self.name = name
        self.section = section
        self.msg = "Required configuration option '%s' (in the '%s' section) not defined!" % (self.name, self.section.upper())

    def __str__(self):
        return self.msg


def error(msg):
    """ Just print error to STDERR.
    """
    sys.stderr.write("%s error: %s\n" % (sys.argv[0].split('/')[-1:][0], msg))

def errexit(msg):
    """ Print error to STDERR and exit program.
    """
    error(msg)
    sys.exit(1)  # python 2.4 compatibility

def okexit(msg=""):
    """ Print message and exit with normal status.
    """
    print msg
    sys.exit(0)  # python 2.4 compatibility
    
def confirmed(msg="YES/NO?"):
    """ Ask for confirmation. Repeat question until user answered YES or NO.
    """
    print msg,
    while 1:
        try:
            answer = raw_input().lower()
        except:  # prevent interrupting by ^D (EOF)
            # but you must handle ^C and other signals outside this function!
            answer = ''
        if answer == 'yes':
            return True
        elif answer == 'no' or answer == 'n':
            return False
        print "Answer YES or NO."
    
def rootcheck():
    """ Are you root now?
    """
    return not os.getuid()

def pwgen(size=12):
    """ Very simple password generator
    """
    return ''.join([choice(string.letters + string.digits) for i in range(size)])

def sanity(text, length=0):
    """ Translate any string to ASCII and optionally restrict length.
    Very dummy algorigthm yet.
    """
    if not length:
        length = len(text)
    return text.replace('.', '_').replace('-', '_')[0:length]

def sanity_host(host):
    """ Check for input valid hostname or ip address.
    """    
    return host  # TODO Well, I'll do it tomorrow.

def tail(fd, nol=10, read_size=1024, grep=''):
    """
    This function returns the last N lines of a file.
    Args:
        fd: file object
        nol: number of lines to print
        read_size:  data is read in chunks of this size (optional, default=1024)
    Raises:
        IOError if file cannot be processed.
    Based on recipe by Manu Garg: http://www.manugarg.com/2007/04/real-tailing-in-python.html
    """
    offset = read_size
    fd.seek(0, 2)
    file_size = fd.tell()
    if not file_size:
        return []
    while 1:
        if file_size < offset:
            offset = file_size
        fd.seek(-1*offset, 2)
        read_str = fd.read(offset)
        # Remove newline at the end
        if read_str[offset - 1] == '\n':
            read_str = read_str[:-1]
        if grep:
            lines = [x for x in read_str.split('\n') if x.find(grep)]
        else:
            lines = read_str.split('\n')
        if len(lines) >= nol:  # Got nol lines
            return lines[-nol:]
        if offset == file_size:   # Reached the beginning
            if grep and (read_str.find(grep) + 1):
                return [read_str]
            else:
                return []
        offset += read_size

def addactions(func):
    """ Decorator for running additional actions.
    These are commands defined in the config. They run before and after the some method called.
    """
    def do_ext_actions(*args, **kwargs):
        # TODO get pre and post commands from config (how to know which section?)
        # call pre action here
        # XXX print "Pre action called DEBUG"
        try:
            #print "Function %s called DEBUG" % (func.__name__)
            result = func(*args, **kwargs)
        finally:
            # call post action here
            #print "Post action called DEBUG"
            pass
        return result
    return do_ext_actions


class Config:
    """ Work with configuration of the DrAdm
    """    
    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()
        self.config.read('/etc/dradm/dradmrc')

    """ Precompiled configuration default values
    """
    defaults = {'common':
                {
                    'tmp': '/tmp',
                 },
                'apache':
                {
                    'service': '/etc/init.d/apache2',
                    'vhostroot': '/etc/apache2/vhosts.d',
                    'port': 80,
                    'template': '/etc/dradm/vhost-apache',
                    'htdir': 'htdocs',
                    'cgidir': 'cgi-bin',
                    'logroot': '/var/log/vhosts.d/%(PROJECT)s',
                    'errorlog': '%(SITENAME)s-apache-error.log',
                    'accesslog': '%(SITENAME)s-apache-access.log',
                 },
                'backup':
                {
                    'files_path': '/var/arc/files',
                    'mysql_backup': '/usr/local/sbin/mysqlbackup',
                    'mysql_path': '/var/arc/mysql',
                    'mysql_file': '%(DBNAME)s-%(DATE)s',
                    'arc': 'gzip',  # gzip and bzip2 formats recognized
                 },
                'changelog':
                {
                    'news': 1,  # display host news? (0/1 - False/True)
                    'path': '/var/log',  # path to changelog file
                    'lines': 3,  # how much lines of each type to display?
                 },
                'mysql':
                {
                    'host': 'localhost',
                    'user': 'root',
                 },
                'nginx':
                {
                    'service': '/etc/init.d/nginx',
                    'vhostroot': '/etc/nginx/vhosts.d',
                    'port': 80,
                    'template': '/etc/dradm/vhost-nginx',
                    'htdir': 'htdocs',
                    'cgidir': 'cgi-bin',
                    'logroot': '/var/log/vhosts.d/%(PROJECT)s',
                    'errorlog': '%(SITENAME)s-nginx-error.log',
                    'accesslog': '%(SITENAME)s-nginx-access.log',             
                 },
                'project':
                {
                    'root': '/var/www',
                    'pre_add': '',
                    'post_add': '',
                    'pre_drop': '',
                    'post_drop': '',
                 },
                'system':
                {
                    'acl': 1,  # 1/0 - ACL supported YES/NO
                    'addgroup_cmd': '/usr/sbin/groupadd',
                    'delgroup_cmd': '/usr/sbin/groupdel',
                    'adduser_cmd': '/usr/sbin/useradd',
                    'deluser_cmd': '/usr/sbin/userdel',
                    'moduser_cmd': '/usr/sbin/usermod',
                    'shell': '/bin/bash',
                 }
                }

    def security(self):
        """ Checks access rights to config directory and config file.
        """
        root_uid = root_gid = 0  # right afaik for all unicies
        if not os.path.exists('/etc/dradm/dradmrc'):
            raise UtilityError("DrAdm1 config not defined! Program aborted.")
        for tested_file, right_mode in (('/etc/dradm', 16888), ('/etc/dradm/dradmrc', 33272)):
            try:
                stats = os.stat(tested_file)
                if stats[4] != root_uid or stats[5] != root_gid:
                    error("%s owner was unproperly setted. It corrected. Be aware!" % tested_file)
                    os.chown(tested_file, root_uid, root_gid)
                if stats[0] != right_mode:
                    error("%s access mode was unproperly setted. It corrected. Be aware!" % tested_file)
                    os.chmod(tested_file, right_mode)
            except:
                raise UtilityError("Error on correcting access rights to %s. Program aborted." % tested_file)

    def get(self, section='', name=''):
        if not section and not name:
            return self.config
        else:
            try:
                return self.config.get(section, name)
            except ConfigParser.NoSectionError:
                try:
                    return Config.defaults[section.lower()][name.lower()]
                except:
                    raise ConfigError(name, section)
            except ConfigParser.NoOptionError:
                try:
                    return Config.defaults[section.lower()][name.lower()]
                except:
                    raise ConfigError(name, section)


if __name__ == "__main__":
    print rootcheck()
    print pwgen()
    print sanity('test'), sanity('test Yes123-3_/*8')
    testconf = Config()
    testconf.get('test', 'test')
    print testconf
