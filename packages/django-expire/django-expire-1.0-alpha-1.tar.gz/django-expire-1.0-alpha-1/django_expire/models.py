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
        ordering = ('-date_logged',)

    def __unicode__(self):
        return 'Logged session %Y-%m-%d %H:%M'
