import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

FTP_MODE_UPLOAD = 0
FTP_MODE_DOWNLOAD = 1
FTP_MODE_DELETE = 2

FTP_MODE = (
    (FTP_MODE_UPLOAD, _('Upload')),
    (FTP_MODE_DOWNLOAD, _('Download')),
    (FTP_MODE_DELETE, _('Delete')),
)
FTP_COMMAND_MODE = {
    'STOR': FTP_MODE_UPLOAD,
    'RETR': FTP_MODE_DOWNLOAD,
    'DELE': FTP_MODE_DELETE,
}

class FTPUserGroup(models.Model):
    name = models.CharField(_('Group name'), null=False,
            blank=False, max_length=100)
    home_directory = models.CharField(_('Home directory'), null=False,
            blank=False, max_length=255)
    permission = models.CharField(_('Permission'),
            null=False, blank=False, max_length=8, default='elradfmw')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('FTP user group')
        verbose_name_plural = _('FTP user groups')

def replace_special_name(self, path, ftpuser):
    """
    get_directory_handler
    replace special name.
    """
    path = path.replace('<username>', ftpuser.user.username)
    return path

class FTPUser(models.Model):
    user = models.OneToOneField(User, verbose_name=_('User'),
            null=False, blank=False)
    usergroup = models.ForeignKey(FTPUserGroup,
            verbose_name=_('FTP user group'), null=False, blank=False)
    last_login = models.DateTimeField(_('Last login'),
            default=datetime.datetime.now, editable=False)

    get_directory_handler = replace_special_name

    def __unicode__(self):
        try:
            user = self.user
        except:
            user = None
        return user and user.username

    def _get_home_directory(self):
        dir_path = self.usergroup.home_directory
        if self.get_directory_handler:
            return self.get_directory_handler(dir_path, self)
        return dir_path
    home_directory = property(_get_home_directory)

    def check_password(self, password):
        return self.user.check_password(password)

    def has_perm(self, perm, path):
        """
        permission test.
        """
        return perm in self.get_perms()

    def get_perms(self):
        """
        return permission string.
        """
        return self.usergroup.permission

    def login_update(self):
        self.last_login = datetime.datetime.now()

    @classmethod
    def get_user(cls, username):
        try:
            return cls.objects.get(user__username=username)
        except ObjectDoesNotExist:
            pass

    class Meta:
        verbose_name = _('FTP user')
        verbose_name_plural = _('FTP users')

class FTPLog(models.Model):
    user = models.ForeignKey(FTPUser, verbose_name=_('FTP user'))
    mode = models.IntegerField(_('Mode'), null=False,
            blank=False, choices=FTP_MODE)
    filename = models.CharField(_('Filename'), blank=True,
            max_length=255)
    remote_path = models.CharField(_('Remote path name'),
            blank=True, max_length=1024)
    local_path = models.CharField(_('Local path name'),
            blank=True, max_length=1024)
    created_at = models.DateTimeField(_('Created at'),
            blank=False, default=datetime.datetime.now, editable=False)

    def __unicode__(self):
        return self.filename

    @classmethod
    def logging(cls, *args, **kwargs):
        kwargs['mode'] = FTP_COMMAND_MODE[kwargs['mode']]
        cls.objects.create(*args, **kwargs)

    class Meta:
        verbose_name = _('FTP log')
        verbose_name_plural = _('FTP logs')
        ordering = ('-created_at',)    
