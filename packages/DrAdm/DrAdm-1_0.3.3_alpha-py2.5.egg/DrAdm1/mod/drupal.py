#!/usr/bin/env python

# DrAdm1 utilities pack - www.dradm.org
# 2009 (c) Axel <dev@axel.pp.ru>
# Under GPL v3

import shutil
from subprocess import *
from utils import *


class DrupalInstall:
    """ Controls a system Drupal installation.
    """
    def __init__(s, config):
        pass

    def core_add(s, vers='stable'):
        """ Setup files for Drupal core
        """
        pass

    def core_check(s):
        """ Check for updates of the Drupal core
        """
        pass

    def core_update(s):
        """ Update Drupal core files to latest version
        """
        pass

    def core_set_default(s):
        """ Set default version of the Drupal core
        """
        pass

    def module_add(s):
        pass

    def theme_add(s):
        pass

    def module_check(s):
        """ Check for updates
        """
        pass

    def module_update(s):
        pass

    def theme_check(s):
        """ Check for updates
        """
        pass

    def theme_update(s):
        pass

    def module_drop(s):
        pass

    def theme_drop(s):
        pass

    
class DrupalHost:
    """ Controls a virtual host Drupal instance.
    """
    def __init__(s, config, site, project=''):
        pass

    def add(s):
        """ Setup links"""
        pass

    def drop(s):
        pass

    def enable(s):
        """ Set site online """
        pass
    
    def disable(s):
        """ Set site offline """
        pass

    def update(s):
        pass


