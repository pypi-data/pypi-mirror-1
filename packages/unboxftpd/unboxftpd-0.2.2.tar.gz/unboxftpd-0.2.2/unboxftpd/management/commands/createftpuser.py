import sys

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist

from unboxftpd.models import FTPUser, FTPUserGroup

class Command(BaseCommand):
    """
    addftpuser command.

    syntax:
        manage.py addftpuser [options] username groupname
    
    'username' user and 'groupname' ftpusergroup should be existing.
    """

    args = 'username groupname'

    def handle(self, *args, **options):
        # read arguments.
        if len(args) is not 2:
            sys.stdout.write('Require two arguments, "username" and "groupname".\n')
            exit()

        username, groupname = args
        # user
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            sys.stdout.write('No such user "%s".\n' % username)
            exit()

        # group
        try:
            group = FTPUserGroup.objects.get(name=groupname)
        except ObjectDoesNotExist:
            sys.stdout.write('No such ftp user group "%s".\n' % groupname)
            exit()

        # create ftp user
        FTPUser.objects.create(user=user, usergroup=group)
        sys.stdout.write('Ftp user "%s" was created.\n' % username)
