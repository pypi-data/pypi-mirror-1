from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.syndication.feeds import Feed

from models import FTPLog, FTP_MODE

FTP_LOG_FEED_NUM = getattr(settings, 'FTP_LOG_FEED_NUM', 100)

class FTPLogFeed(Feed):
    title = _('FTPD log')
    description = _('FTPD log feeds.')
    log_model = FTPLog
    mode = None
    num_output = FTP_LOG_FEED_NUM
    link = ''
    item_link = ''
    title_template = 'feeds/ftplog_title.html'
    description_template = 'feeds/ftplog_description.html'

    def items(self):
        logs = self.log_model.objects.all()
        if self.mode:
            logs = logs.filter(mode=self.mode)
        return logs[:self.num_output]

    def item_pubdate(self, item):
        return item.created_at

    def item_author_name(self, item):
        return item.user
