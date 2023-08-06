#import pickle
try:
    from hashlib import sha1
except ImportError:
    from sha import new as sha1
import time
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.utils import simplejson

from account import settings as app_settings


class AuthKey(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    uid = models.PositiveIntegerField()
    expired = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    data = models.TextField()

    def __unicode__(self):
        return 'Key for %s' % self.username

    def export_data(self):
        return simplejson.loads(self.data)

    def import_data(self, **kwargs):
        pairs = kwargs#[]
        #for key, value in kwargs.iteritems():
            #if isinstance(value, unicode):
                #value = value.encode('utf-8')
            #if isinstance(value, datetime):
                #value = strftime(value)
            #pairs.append((key, value))
        self.data = simplejson.dumps(dict(pairs))

    def save(self, *args, **kwargs):
        if not self.id:
            source = '%s%d%d' % (settings.SECRET_KEY, time.time(), id({}))
            self.id = sha1(source).hexdigest()
        if not self.expired:
            self.expired = datetime.now() + timedelta(seconds=app_settings.AUTH_KEY_TIMEOUT)
        super(AuthKey, self).save(*args, **kwargs)


#def strftime(when):
    #return when.strftime('%d-%m-%y-%H-%M-%S')


#def strptime(when):
    #try:
        #return datetime.fromtimestamp(time.mktime(
            #time.strptime(when, '%d-%m-%y-%H-%M-%S')))
    #except ValueError:
        #return None


