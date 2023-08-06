"""
DrAdm1 utilities pack - www.dradm.org
2009 (c) Axel <dev@axel.pp.ru>
Under GPL v3

Variables used in templates as '%(VARNAME)s':
 ACCESSLOG
 ALIASES
 CGIROOT
 EMAIL
 ERRORLOG
 LOGROOT
 PORT
 SITENAME
 WWWROOT
"""

import os, shutil
from subprocess import *
from utils import *


class VhostError(Exception):
    def __init__(self, vhost, msg=''):
        self.type = vhost.section
        self.name = vhost.name
        self.project = vhost.project
        self.msg = msg
        if not self.msg:
            self.msg = "Operation error in 'virtual host' module."

    def __str__(self):
        return self.msg


class ApacheVhost:
    """ Work with Apache virthost configs (in separated files)
    """
    def __init__(self, config, name, project=''):
        self.section = 'APACHE'
        self.service =  config.get(self.section, 'service')
        self.port = config.get(self.section, 'port')
        self.vhostroot = config.get(self.section, 'vhostroot')
        self.prjroot = config.get('Project', 'root')
        self.htdir = config.get(self.section, 'htdir')
        self.cgidir = config.get(self.section, 'cgidir')
        self.logroot = config.get(self.section, 'logroot')
        self.accesslog = config.get(self.section, 'accesslog')
        self.errorlog = config.get(self.section, 'errorlog')
        try:
            self.template_name = config.get(self.section, 'template')
            self.template = open(self.template_name).read()
        except IOError:
            raise VhostError(self, "Template for Apache vhost not found or not readable!")
        self.name = name
        self.project = project
        if project:
            self.confname = "%s-%s.conf" % (self.project, self.name)
            self.realname = "%s/%s" % (self.project, self.name)
            self.hostpath = os.path.join(self.prjroot, self.project, self.name)  # base path for the host
            self.prjpath = os.path.join(self.prjroot, self.project)  # base path for the project
        else:
            self.confname = "%s.conf" % self.name
            self.realname = self.name
            self.prjpath = self.hostpath = os.path.join(self.prjroot, self.name)

    def exists(self):
        """ Is this virtual host exists?
        """
        return os.path.exists(self.prjpath) and os.path.exists(self.confname)            

    @addactions
    def add(self):
        tempvars = {
            'SITENAME': self.name,
            'ALIASES': "www.%s" % self.name,
            'EMAIL': "webmaster@%s" % self.name,
            'PORT': self.port,
            'LOGROOT': self.logroot,
            'ERRORLOG': self.errorlog,
            'ACCESSLOG': self.accesslog,
            'PROJECT': self.project,
            'SITEROOT': self.hostpath
            'CGIROOT': "%s/%s/%s" % (self.prjroot, self.realname, self.cgidir),
            'WWWROOT': "%s/%s/%s" % (self.prjroot, self.realname, self.htdir),
            }
        try:
            vhost_conf = self.template % tempvars % tempvars
        except ValueError:
            raise VhostError(self, "problem in the %s template!" % self.template_name)
        # make vhost dirs
        try:
            os.mkdir(self.hostpath)
            os.chdir(self.hostpath)
            os.mkdir(self.htdir)
            os.mkdir(self.cgidir)
        except:
            raise VhostError(self, "Virtual host %s already exists." % self.name)
        try:
            os.mkdir(self.vhostroot)
        except OSError:
            pass  # is path exists? it is not a problem
        try:
            os.chdir(self.vhostroot)
        except OSError:
            raise VhostError(self, "Can't change directory to %s" % self.vhostroot)
        if os.path.exists(self.confname) and not os.path.exists("%s.bak-by-dradm" % self.confname): # made backup once
            shutil.move(self.confname, "%s.bak-by-dradm" % self.confname)
        try:
            vhost = open(self.confname, 'w')
            vhost.write(vhost_conf)
            vhost.close()
        except OSError:
            raise VhostError(self, "Can't write config %s" % self.confname)
        try:
            os.mkdir(os.path.join(self.logroot, self.project))
        except:
            pass  # no problems if path already exists                

    @addactions
    def drop(self):
        try:
            os.chdir(self.vhostroot)
        except OSError:
            error("Can't change directory to %s" % self.vhostroot)
        if os.path.exists("%s" % self.confname):
            os.unlink("%s" % self.confname)
        if os.path.exists("%s-disabled" % self.confname):
            os.unlink("%s-disabled" % self.confname)
        call([self.service, 'reload'])

    def enable(self):
        try:
            os.chdir(self.vhostroot)
        except OSError:
            raise VhostError(self, "Can't change directory to %s" % self.vhostroot)
        if os.path.exists("%s-disabled" % self.confname):
            shutil.move("%s-disabled" % self.confname, self.confname)
        call([self.service, 'reload'])
    
    def disable(self):
        try:
            os.chdir(self.vhostroot)
        except OSError:
            raise VhostError(self, "Can't change directory to %s" % self.vhostroot)
        if os.path.exists(self.confname):
            shutil.move(self.confname, "%s-disabled" % self.confname)
        call([self.service, 'reload'])


class NginxVhost:
    """ Work with Nginx virthost configs (in separated files)
    """
    def __init__(self, config, name, project=''):
        self.section = 'NGINX'

    # TODO methods for Nginx


class Vhost:
    def __init__(self, config, name, project='', server_type='APACHE'):
        self.section = 'VHOST'
        self.server_type = server_type.upper()
        if not server_type or self.server_type == 'APACHE':
            self.server = ApacheVhost(config, name, project)
        elif self.server_type == 'NGINX':
            self.server = NginxVhost(config, name, project)
        else:
            raise VhostError(self, "The %s webserver type don't supported." % self.server_type)
        self.name = name
        self.project = project

    @addactions
    def add(self):
        self.server.add()

    @addactions
    def drop(self):
        self.server.drop()

    def enable(self):
        self.server.enable()

    def disable(self):
        self.server.disable()


if __name__ == '__main__':
    """ Quick unit test
    """
    if not rootcheck():
        error("You need run this utility as root!")
    config = Config()
    test = ApacheVhost(config, 'example.com')
    test.add()
    test.disable()
    test.enable()
    test.drop()
    print "Apache vhost tested"
    test = Vhost(config, 'example.com')
    test.add()
    test.disable()
    test.enable()
    test.drop()
    print "Default vhost (apache) tested"
    



