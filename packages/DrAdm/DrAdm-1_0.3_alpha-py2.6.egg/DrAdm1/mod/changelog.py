"""
DrAdm1 utilities pack - www.dradm.org
(c) Axel <dev@dradm.org>
Under GPL v3
"""

import os.path, time
from utils import *


class ChangelogError(Exception):
    def __init__(self, obj, msg=''):
        Exception.__init__(self)
        self.type = obj.section
        self.source = obj.source
        self.project = obj.project
        self.msg = msg or "Operation error in 'changelog' module."
        
    def __str__(self):
        return self.msg


class Changelog:
    """ Work with host changelog.
    Changelog is text file with tab-separated fields:
    TIMESTAMP
    UID - now always root
    SOURCE
    PROJECT
    MESSAGE
    """
    def __init__(self, config, source, project=''):
        self.section = 'CHANGELOG'
        self.source = source
        self.project = project
        self.news = config.get(self.section, 'news')  # display host news in other utilities?
        self.lines = config.get(self.section, 'lines')  # how much lines of each type to display?
        self.path = config.get(self.section, 'path')  # path to changelog file
        try:
            self.file = open(os.path.join(self.path, 'changelog'), 'a+')
        except:
            raise ChangelogError(self, "Can't open host changelog.")

    def project_set(self, project):
        self.project = project

    @addactions
    def add(self, msg):
        """ Add record to changelog.
        """
        # TODO add check for same last record
        if msg:
            self.file.write("%s\t%s\t%s\t%s\t%s\n" % (time.time(), 0,
                                                      self.source, self.project,
                                                      msg.strip().replace("\n", "\\n")))  # uid always = 0 for DrAdm1
            self.file.flush()

    def log_get(self):
        """ Get all changelog as iterator.
        """
        return self.file

    def log_print(self, filter_str=''):
        """ Print last N records to default output.
        """
        for rec in tail(self.file, self.lines, grep=filter_str):
            try:
                stamp, uid, source, project, msg = rec.split('\t')                
                if project:
                    print "%s (%s): %s" % (time.ctime(float(stamp)), project, msg)
                else:
                    print "%s: %s" % (time.ctime(float(stamp)), msg)

            except:
                ChangelogError(self, "Error reading host changelog.")
        self.file.seek(0)

    def record_get(self):
        """ Get one record from the changelog.
        """
        return self.file.readline()

    def record_print(self):
        """ Print one record from the changelog.
        """
        print self.file.readline()

    @addactions
    def host_news(self):
        """ Display last N items (as defined in the config) from changelog.
        """
        return ''

    @addactions
    def project_news(self):
        """ Display last N items related to selected project.
        """
        pass

    @addactions
    def utility_news(self):
        """ Display last N items related to selected utility.
        """
        pass
