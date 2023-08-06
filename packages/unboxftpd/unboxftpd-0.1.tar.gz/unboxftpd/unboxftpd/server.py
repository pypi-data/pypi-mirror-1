import os
import sys
import time
import stat

try:
    import pwd
    import grp
except ImportError:
    pwd = grp = None

from django.conf import settings
from django.utils.encoding import smart_unicode

try:
    from pyftpdlib.ftpserver import FTPHandler, AbstractedFS
except ImportError:
    print 'Please install Python FTP server library(pyftpdlib).\n' \
          'http://code.google.com/p/pyftpdlib/'
    exit()

from unboxftpd.models import FTPUser, FTPLog

class ExtendedFS(AbstractedFS):

    def format_mlsx(self, basedir, listing, perms, facts, ignore_err=True):
        """
        optimize encoding
        this method called by MLSD command.
        """
        permdir = ''.join([x for x in perms if x not in 'arw'])
        permfile = ''.join([x for x in perms if x not in 'celmp'])
        if ('w' in perms) or ('a' in perms) or ('f' in perms):
            permdir += 'c'
        if 'd' in perms:
            permdir += 'p'
        type = size = perm = modify = create = unique = mode = uid = gid = ""
        for basename in listing:
            file = os.path.join(basedir, basename)
            try:
                st = self.stat(file)
            except OSError:
                if ignore_err:
                    continue
                raise
            # type + perm
            if stat.S_ISDIR(st.st_mode):
                if 'type' in facts:
                    if basename == '.':
                        type = 'type=cdir;'
                    elif basename == '..':
                        type = 'type=pdir;'
                    else:
                        type = 'type=dir;'
                if 'perm' in facts:
                    perm = 'perm=%s;' %permdir
            else:
                if 'type' in facts:
                    type = 'type=file;'
                if 'perm' in facts:
                    perm = 'perm=%s;' %permfile
            if 'size' in facts:
                size = 'size=%s;' %st.st_size  # file size
            # last modification time
            if 'modify' in facts:
                try:
                    modify = 'modify=%s;' %time.strftime("%Y%m%d%H%M%S",
                                           time.localtime(st.st_mtime))
                # it could be raised if last mtime happens to be too old
                # (prior to year 1900)
                except ValueError:
                    modify = ""
            if 'create' in facts:
                # on Windows we can provide also the creation time
                try:
                    create = 'create=%s;' %time.strftime("%Y%m%d%H%M%S",
                                           time.localtime(st.st_ctime))
                except ValueError:
                    create = ""
            # UNIX only
            if 'unix.mode' in facts:
                mode = 'unix.mode=%s;' %oct(st.st_mode & 0777)
            if 'unix.uid' in facts:
                uid = 'unix.uid=%s;' %st.st_uid
            if 'unix.gid' in facts:
                gid = 'unix.gid=%s;' %st.st_gid
            # We provide unique fact (see RFC-3659, chapter 7.5.2) on
            # posix platforms only; we get it by mixing st_dev and
            # st_ino values which should be enough for granting an
            # uniqueness for the file listed.
            # The same approach is used by pure-ftpd.
            # Implementors who want to provide unique fact on other
            # platforms should use some platform-specific method (e.g.
            # on Windows NTFS filesystems MTF records could be used).
            if 'unique' in facts:
                unique = "unique=%x%x;" %(st.st_dev, st.st_ino)

            #yield "%s%s%s%s%s%s%s%s%s %s\r\n" %(type, size, perm, modify, create,
            #                                    mode, uid, gid, unique, basename)

            # opts encoding
            line = u"%s%s%s%s%s%s%s%s%s %s\r\n" %(type, size, perm, modify, create,
                                                 mode, uid, gid, unique, smart_unicode(basename))
            yield line.encode('utf8')

class Authorizer(object):
    """
    Authorizer class by FTPUser model.
    """
    user_class = FTPUser

    def get_user(self, username):
        return self.user_class.get_user(username)

    def validate_authentication(self, username, password):
        user = self.get_user(username)
        return not not (user and user.check_password(password))

    def impersonate_user(self, username, password):
        pass    

    def terminate_impersonation(self):
        pass

    def has_user(self, username):
        return self.get_user(username)

    def get_home_dir(self, username):
        user = self.get_user(username)
        # return ascii
        return user and str(user.home_directory)

    def get_msg_login(self, username):
        user = self.get_user(username)
        if user:
            user.login_update()
        return 'welcome.'

    def get_msg_quit(self, username):
        return 'good bye.'

    def has_perm(self, username, perm, path=None):
        user = self.get_user(username)
        return user and user.has_perm(perm, path)

    def get_perms(self, username):
        user = self.get_user(username)
        return user and user.get_perms()

class LoggingHandler(object):
    log_class = FTPLog
    user_class = FTPUser

    def __call__(self, ftp_handler, line, mode):
        """
        logging handler
        """
        user = self.user_class.get_user(ftp_handler.username)

        # TODO detect or force convert
        #if ftp_handler.is_client_utf8:
        #    line = unicode(line, 'utf-8')

        remote_path = ftp_handler.fs.fs2ftp(line)

        if user:
            self.log_class.logging(
                user=user,
                mode=mode,
                filename=smart_unicode(os.path.basename(line)),
                remote_path=smart_unicode(remote_path),
                local_path=smart_unicode(line)
            )

class LoggingFTPHandler(FTPHandler):
    """
    FTPHandler with simple logging.
    """
    logging_handler = LoggingHandler
    is_client_utf8 = False
    default_encoding = 'UTF-8'

    def __init__(self, *args, **kwargs):
        FTPHandler.__init__(self, *args, **kwargs)
        if self.logging_handler:
            self._logging = LoggingHandler()
        if self.get_encoding() == 'UTF-8':
            self._extra_feats += ['UTF8']

    def ftp_STOR(self, line, mode='w'):
        """
        upload
        """
        FTPHandler.ftp_STOR(self, line, mode=mode)
        self.logging(line, 'STOR')

    def ftp_RETR(self, line):
        """
        download
        """
        FTPHandler.ftp_RETR(self, line)
        self.logging(line, 'RETR')

    def ftp_DELE(self, line):
        """
        delete
        """
        FTPHandler.ftp_DELE(self, line)
        self.logging(line, 'DELE')

    def ftp_OPTS(self, line):
        """
        opts for utf8 encoding.
        """
        if line.count(' ') == 1:
            cmd, arg = line.upper().split(' ')
            if cmd == 'UTF8' and arg == 'ON' and  \
                    self.get_encoding() == 'UTF-8':
                self.is_client_utf8 = True
                self.respond('200 OK.')
                return
        FTPHandler.ftp_OPTS(self, line)

    def get_encoding(self):
        return self.default_encoding

    def logging(self, line, mode):
        if self.logging_handler:
            try:
                self._logging(ftp_handler=self, line=line, mode=mode)
            except:
                if settings.DEBUG:
                    raise
