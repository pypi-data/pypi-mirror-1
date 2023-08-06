from django.contrib import admin
from models import *

class LocationAdmin(admin.ModelAdmin):
    model = Location
    list_display = ('name', 'parent', 'base_url', 'target_url')
    fieldsets = (
        (None, {
            'fields': ('name', 'base_url', 'target_url')
        }),
        ('Advanced options', {
            'fields': ('parent', 'order', 'hidden')
        }),
    )

admin.site.register(Location, LocationAdmin)