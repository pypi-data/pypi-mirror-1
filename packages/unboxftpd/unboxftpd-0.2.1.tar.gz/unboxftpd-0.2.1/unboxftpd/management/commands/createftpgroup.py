import sys
import os
from optparse import make_option

from django.core.management.base import BaseCommand
from django.db.models import ObjectDoesNotExist

from unboxftpd.models import FTPUserGroup

class Command(BaseCommand):
    """
    addftpgroup command.

    syntax:
        manage.py createftpgroup [options] groupname home_directory
    
    """
    option_list = BaseCommand.option_list + (
        make_option('--permission', type='string',
                dest='permission', help='permission for home_directory.'),
    )
    args = 'groupname home_directory'

    def handle(self, *args, **options):
        # read arguments.
        if len(args) is not 2:
            sys.stdout.write('Require two arguments.\n' \
                             'Please see manage.py help addftpgroup.\n')
            exit()

        groupname, home_directory = args

        # create ftp user
        ftpusergroup = FTPUserGroup(name=groupname, home_directory=home_directory)

        # set permission
        if options['permission']:
            ftpusergroup.permission = options['permission']

        ftpusergroup.save()

        sys.stdout.write('Ftp user group "%s" was created.\n' % groupname)
