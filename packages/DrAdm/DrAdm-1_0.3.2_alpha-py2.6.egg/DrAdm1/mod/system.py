"""
 DrAdm1 utilities pack - www.dradm.org
 2009 (c) Axel <dev@axel.pp.ru>
 Under GPL v3

 TODO replace setfacl utility call with posix1e functions
"""


import sys
#import posix1e
from subprocess import *
from utils import *


class SysError(Exception):
    """ Display errors for system user module
    """
    def __init__(self, obj, msg=''):
        self.type = obj.section
        self.name = obj.name
        self.project = obj.project
        self.msg = msg
        if not self.msg:
            self.msg = "Operation error in 'system user' module."

    def __str__(self):
        return self.msg


class SysGroup:
    """ Works with system groups and ACLs.
    """
    def __init__(self, config, name):
        self.section = 'SYSTEM'
        self.name = name  # may consists of: ._-0-9a-z
        self.project = name  # by design
        self.acl = config.get(self.section, 'acl')
        self.addgroup = config.get(self.section, 'addgroup_cmd')
        self.delgroup = config.get(self.section, 'delgroup_cmd')
        
    def exists(self):
        """ Check is the group exists in the system?
        """
        for rec in open('/etc/group'):
            if rec.split(':')[0] == self.name:
                return True
        return False
    
    @addactions
    def add(self):
        """ Add new group to the system.
        """
        rc = call([self.addgroup, self.name])
        if rc:
            return rc

    def getname(self):
        return self.name

    def list(self):
        """ Get list of all defined groups.
        """
        pass

    def list_print(self):
        """ Print list of all defined groups.
        """
        pass

    @addactions
    def drop(self):
        """ Delete group from the system.
        """
        return not call([self.delgroup, self.name])

    @addactions
    def modify(self):
        pass

    @addactions
    def acl_set(self, path, mode="rwx", recursive=True):
        call(['setfacl', (recursive and '-R' or ''), '-m', 'g:%s:%s' % (self.name, mode), '%s' % path])


class SysUser:
    """ Work with system accounts and ACLs.
    """
    def __init__(self, config, name, project='', group='', home='', shell='/bin/bash'):
        self.section = 'SYSTEM'
        self.name = name  # may consists of: _-0-9a-z
        self.home = home
        if group:
            self.group_name = group
        elif project:
            self.group_name = project
        else:
            self.group_name = name
        self.group = SysGroup(config, self.group_name)
        self.project = project
        self.acl = config.get(self.section, 'acl')
        self.adduser = config.get(self.section, 'adduser_cmd')
        self.deluser = config.get(self.section, 'deluser_cmd')
        self.moduser = config.get(self.section, 'moduser_cmd')
        if not shell:
            self.shell = config.get(self.section, 'shell')
        else:
            self.shell = shell
        self.pwd = ''

    def exists(self):
        """ Is this user exists?
        """
        for rec in open('/etc/passwd'):
            if rec.split(':')[0] == self.name:
                return True
        return False

    @addactions
    def add(self):
        if not self.home:
            self.home = '/home/%s' % self.name
        try:
            if not self.group.exists():
                self.group.add()
            rc = call([self.adduser, '-d%s' % self.home, '-g%s' % self.group.getname(), '-s%s' % self.shell, self.name])
        except:
            raise SysError(self, "Can't run `%s` utility." % self.adduser)
        self.pwd = pwgen()
        try:
            pwd_set = Popen('/usr/bin/passwd %s' % self.name, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            pwd_set.communicate(self.pwd + '\n' + self.pwd + '\n')
        except:
            raise SysError(self, "Can't set password with `passwd` utility.")

    def getname(self):
        return self.name

    def getpasswd(self):
        return self.pwd

    def gethome(self):
        return self.home
        
    def list(self):
        pass

    def list_print(self):
        pass

    @addactions
    def drop(self):
        return not call([self.deluser, self.name])

    @addactions
    def modify(self):
        if not self.home:
            self.home = '/home/%s' % self.name
        try:
            if not self.group.exists():
                self.group.add()
            rc = call([self.moduser, '-d%s' % self.home, '-s%s' % self.shell, '-G%s' % self.group.getname(), self.name])
        except:
            raise SysError(self, "Can't run `%s` utility." % self.moduser)

    @addactions
    def acl_set(self, path, mode="rwx", recursive=True):
        call(['setfacl', (recursive and '-R' or ''), '-m', 'u:%s:%s' % (self.name, mode), '%s' % path])        


if __name__ == '__main__':
    """ Quick unit test
    """
    if not rootcheck():
        error("You need run this utility as root!")
    config = Config()
    test = SysUser(config, 'test1314', '', shell='/sbin/nologin')
    print test.exists()
    if test.add():
        print "Test user created."
    print test.exists()
    if test.drop():
        print "Test user deleted."
