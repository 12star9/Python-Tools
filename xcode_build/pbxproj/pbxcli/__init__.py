from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()


import os
from pbxproj.XcodeProject import XcodeProject


def open_project(args):
    if os.path.isdir(args[u'<project>']):
        args[u'<project>'] += u"/project.pbxproj"

    if not os.path.isfile(args[u'<project>']):
        raise Exception(u'Project file not found')

    return XcodeProject.load(args[u'<project>'])


def backup_project(project, args):
    if args[u'--backup']:
        return project.backup()
    return None


def resolve_backup(project, backup_file, args):
    # remove backup if everything was ok.
    if args[u'--backup'] and backup_file:
        os.remove(backup_file)


def command_parser(command, auto_save=True):
    def parser(args):
        try:
            project = open_project(args)
            backup_file = backup_project(project, args)
            print(command(project, args))
            if auto_save:
                project.save()
            resolve_backup(project, backup_file, args)
        except Exception as ex:
            print(u"{0}".format(ex))
            exit(1)
    return parser
