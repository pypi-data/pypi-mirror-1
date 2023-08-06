import os
import sys
import datetime
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.daemonize import become_daemon

from unboxftpd.server import FTPServer, ExtendedFS, Authorizer, LoggingFTPHandler

FTPD_DEFAULT_SETTINGS = {
    'FTPD_ADDRESS': 'localhost',
    'FTPD_PORT': 21,
    'FTPD_LOG': None,
    'FTPD_ERROR_LOG': None,
    'FTPD_MASQUERADE_ADDRESS': None,
    'FTPD_PASSIVE_PORTS': None,
}

def get_settings(name):
    return getattr(settings, name, FTPD_DEFAULT_SETTINGS[name])

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--daemonize', action='store_true',
                dest='daemonize', help='FTPD become daemon'),
        make_option('--no-logging', action='store_false',
                dest='no-logging', help='No logging'),
        make_option('--pidfile', default=None,
                dest='pidfile', help='Create PID file'),
        make_option('--pasvport', default=None,
                dest='pasvport', help='Passive ports'),
        make_option('--masquerade-address', default=None,
                dest='masquerade-address', help='masquerade address')
    )
    args = '[optional port number, or ipaddr:port]'

    def handle(self, addrport='', *args, **options):
        # logging
        if options['no-logging']:
            LoggingFTPHandler.logging_handler = None
        LoggingFTPHandler.authorizer = Authorizer()
        LoggingFTPHandler.abstracted_fs = ExtendedFS

        # masquerade_address
        LoggingFTPHandler.masquerade_address = options['masquerade-address'] or \
                get_settings('FTPD_MASQUERADE_ADDRESS')

        # passive ports
        passive_ports = options['pasvport'] or get_settings('FTPD_PASSIVE_PORTS')
        if passive_ports:
            low, high = map(int, passive_ports.split(':'))
            sys.stdout.write('Using passive port %d-%d\n' % (low, high))
            LoggingFTPHandler.passive_ports = range(low, high + 1)

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

        # pidfile
        if options['pidfile']:
            pidfile = open(options['pidfile'], 'w')
            pidfile.write('%d' % os.getpid())
            pidfile.close()
            pidfile = None

        sys.stdout.write('[%s]\nStarting UnboxFTPD\n' % \
                datetime.datetime.now().strftime('%Y%m/%d %H:%m:%S'))
        ftpd.serve_forever()
