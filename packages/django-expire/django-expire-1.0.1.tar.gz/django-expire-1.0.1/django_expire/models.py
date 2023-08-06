from django.db import models
from django.contrib.auth.models import User
import datetime


class LoggedSession(models.Model):
    user = models.ForeignKey(User)
    session_id = models.CharField(max_length=40, db_index=True)
    ip = models.IPAddressField(db_index=True, blank=True, null=True)
    active = models.BooleanField(default=True)
    date_logged = models.DateTimeField(default=datetime.datetime.now(),
                                       editable=False)

    class Meta:
        ordering = ('-date_logged', '-id')

    def __unicode__(self):
        if not self.date_logged:
            date_logged = ''
        else:
            date_logged = self.date_logged.strftime(' %Y-%m-%d %H:%M')
        return u'Logged session %s' % date_logged
