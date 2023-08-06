import sys
import datetime
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.daemonize import become_daemon

try:
    from pyftpdlib.ftpserver import FTPServer
except ImportError:
    from unboxftpd.pyftpdlib.ftpserver import FTPServer

from unboxftpd.server import ExtendedFS, Authorizer, LoggingFTPHandler

FTPD_DEFAULT_SETTINGS = {
    'FTPD_ADDRESS': 'localhost',
    'FTPD_PORT': 21,
    'FTPD_LOG': None,
    'FTPD_ERROR_LOG': None,
}

def get_settings(name):
    return getattr(settings, name, FTPD_DEFAULT_SETTINGS[name])

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--daemonize', action='store_true',
                dest='daemonize', help='FTPD become daemon'),
        make_option('--no-logging', action='store_false',
                dest='no-logging', help='No logging')
    )
    args = '[optional port number, or ipaddr:port]'

    def handle(self, addrport='', *args, **options):
        # logging
        if options['no-logging']:
            LoggingFTPHandler.logging_handler = None
        LoggingFTPHandler.authorizer = Authorizer()
        LoggingFTPHandler.abstracted_fs = ExtendedFS

        # ftp port:addr
        # default localhost:21
        if addrport:
            addr, port = addrport.split(':')
        else:
            addr = get_settings('FTPD_ADDRESS')
            port = get_settings('FTPD_PORT')

        # create server instance
        ftpd = FTPServer((addr, port), LoggingFTPHandler)

        # daemonize
        if options['daemonize']:
            kwargs_daemon = {}
            if get_settings('FTPD_LOG'):
                kwargs_daemon['out_log'] = get_settings('FTPD_LOG')
            if get_settings('FTPD_ERROR_LOG'):
                kwargs_daemon['err_log'] = get_settings('FTPD_ERROR_LOG')

            become_daemon(**kwargs_daemon)

        sys.stdout.write('[%s]\nStarting UnboxFTPD\n' % \
                datetime.datetime.now().strftime('%Y%m/%d %H:%m:%S'))
        ftpd.serve_forever()
