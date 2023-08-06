"""
  DrAdm1 utilities pack - www.dradm.org
  2009 (c) Axel <dev@axel.pp.ru>
  Under GPL v3
"""

import optparse
from mod import changelog, project, system
from mod.utils import *

def main():
    """ Add user to system and optionally to project.
    """
    if not rootcheck():
        errexit("You need superuser privileges!")
    config = Config()
    cli = optparse.OptionParser(description="Create user and optionally add it to the project. Part of DrAdm1 utilities pack. http://dradm.org",
                                version="1.0", usage="%prog [options] <user> [project]")
    cli.add_option("--verbose", "-v", help="verbose output to the console",
                   action="store_true", default=False)
    opt, arg = cli.parse_args()
    try:
        chlog = changelog.Changelog(config, cli.get_prog_name())
    except changelog.ChangelogError, err:
        errexit(err.msg)
    if not arg:
        print chlog.host_news()
        print "Type -h for command help."
        exit()
    try:
        name_arg = sanity(arg[0])
        if len(arg) > 1:
            prj_arg = arg[1]  # don't sanitize project name here, because it may be sitename
            chlog.project_set(prj_arg)
        else:
            prj_arg = ''
    except:
        errexit("Arguments error.")
    try:
        if prj_arg:
            prj = project.Project(config, prj_arg)
            if not prj.exists():
                raise project.ProjectError("Project %s not exists." % prj_arg)
        if prj_arg and prj.exists():
            group = system.SysGroup(config, prj_arg)
            if not group.exists():
                group.add()
                chlog.add("Group %s created." % group.getname())
            user = system.SysUser(config, name_arg, prj_arg, group.getname(), prj.getpath())
        else:
            user = system.SysUser(config, name_arg)
        if not user.exists():
            user.add()
            chlog.add("User %s created." % user.getname())
            print "* User: %s" % user.getname()
            print "* Password: %s" % user.getpasswd()
            print "* Home: %s" % user.gethome()
        else:
            user.modify()
        if prj_arg and prj.exists():
            group.acl_set(prj.getpath())
            chlog.add("User %s granted access to %s project." % (user.getname(), prj.getname()))
            if opt.verbose:
                print "Access for user group `%s` to `%s` project granted." % (group.getname(), prj.getname())
    except project.ProjectError, err:
        errexit(err.msg)
    except system.SysError, err:
        errexit(err.msg)
    except ConfigError, err:
        errexit(err.msg)
    except SystemExit:
        pass
    #except:
    #    errexit("Utility internal error.")


if __name__ == "__main__":
    main()
