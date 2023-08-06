from django.utils.translation import ugettext_lazy as _
from south.db import db
from django.db import models
from django_faces.models import *

class Migration:
    
    def forwards(self):
        
        # Model 'CacheState'
        db.create_table('django_faces_cachestate', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hash', models.CharField( _('Hash'), max_length=32, unique = True)),
            ('enabled', models.BooleanField(_("Avatar enabled"), default=False)),
            ('expire_after', models.DateTimeField(_("Cache expire date"))),
            ('actual_width', models.IntegerField(_('Actual avatar\'s width'), default = 0)),
            ('actual_height', models.IntegerField(_('Actual avatar\'s height'), default = 0)),
        ))
        
        db.send_create_signal('django_faces', ['CacheState'])
    
    def backwards(self):
        db.delete_table('django_faces_cachestate')
        
