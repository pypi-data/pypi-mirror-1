from django.contrib import admin
from object_links.models import *

class LinkAdmin(admin.ModelAdmin):
    list_display = ('display', 'type','active')
    list_filter = ('active', 'type',)
    ordering = ('display',)
    search_fields = ('display', 'external_url')
    
    class Media:
        js = ("object_links/jquery.js","object_links/admin_links.js",)
        
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name','active')
    list_filter = ('active',)
    ordering = ('name',)
    search_fields = ('name', 'description', 'links')
    
admin.site.register(Link, LinkAdmin)
admin.site.register(Menu, MenuAdmin)
