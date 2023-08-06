from django.db import models
from django.db.models import get_model
from django.conf import settings
from object_links.fields import ManyToManyField_NoSyncdb

LINK_TYPES = ((s, s) for s in ('internal', 'external'))
LINKABLE = getattr(settings, 'LINKABLE_MODELS', {})
LINKABLE_CHOICES = ((v, v) for k, v in LINKABLE.iteritems())

class Link(models.Model):
    display = models.CharField(max_length=150, blank=True)
    css_class = models.CharField(max_length=200, blank=True, help_text='optionally apply css class(es) to this link')
    active = models.BooleanField(default=True)
    type = models.CharField(max_length=100, choices=LINK_TYPES, default='internal')
    external_url = models.CharField(max_length=400, blank=True)
    model = models.CharField(max_length=200, choices=LINKABLE_CHOICES, blank=True, help_text='The type of object you want to link to')
    menus = models.ManyToManyField('Menu', db_table='links_link_menus', blank=True, null=True, help_text='Specify which Menus you want this link to appear in.')
    

    def __unicode__(self):
        return self.display

    def _linked_object(self):
        if not self.is_external:
            for k,v in LINKABLE.iteritems():
                if v == self.model:
                    return getattr(self, k)
        return None
    
    def _is_external(self):
        if self.type == 'external':
            return True
        return False
    
    is_external = property(_is_external)
    linked_object = property(_linked_object)

    def get_url(self):
        if self.is_external:
            return self.external_url
        elif self.linked_object:
            url = self.linked_object.get_absolute_url()
            return url
    
#add the dynamic fields to the model
for k, v in LINKABLE.iteritems():
    if not getattr(Link, k, None):
        Link.add_to_class(k, models.ForeignKey(v, blank=True, null=True,
            related_name='object_link'))


class Menu(models.Model):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=200, blank=True)
    css_class = models.CharField(max_length=200, blank=True, help_text='optionally apply css class(es) to this menu')
    active = models.BooleanField(default=True)
    links = ManyToManyField_NoSyncdb('Link', db_table='links_link_menus', blank=True, null=True, help_text='Specify which links show up in this menu.')
    key = models.CharField(max_length=150, blank=True, help_text='An unchanging, unique key. Used for accessing this menu from a template. Also becomes the html id')
    
    def __unicode__(self):
        return self.name

    
