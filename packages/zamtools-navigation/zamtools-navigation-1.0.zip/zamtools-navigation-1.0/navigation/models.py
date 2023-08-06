from django.db import models
from django.core.urlresolvers import reverse
from fields import AutoSlugField

class TopLevelManager(models.Manager):
    def get_query_set(self):
        """
        Returns all top level Locations; any Location without a parent. Hidden 
        locations are ignored.
        """
        return super(TopLevelManager, self).get_query_set().filter(parent=None, hidden=False)

class Location(models.Model):
    """
    Represents a particular location within a site's map.  This map can be 
    built as a hierarchy using the recursive parent location references.
    """
    name = models.CharField(max_length=50, help_text='The text visible in the navigation.')
    slug = AutoSlugField(overwrite_on_save=True)
    base_url = models.CharField(max_length=500, help_text='The smallest unique portion of the url that determines the location. eg: /about/ ')
    target_url = models.CharField(max_length=500, help_text='Go here when clicked. eg: /about/')
    parent = models.ForeignKey('Location', null=True, blank=True, help_text='Optionally group this location under another location.  Assumed to be a top level location if left blank. Does not affect urls.')
    order = models.PositiveSmallIntegerField(null=True, blank=True, help_text='The order the locations appear in when listed, lower numbers come sooner.  By default, locations are sorted in the order they were added.')
    hidden = models.BooleanField(help_text='Prevents the location from being displayed in lists. Also prevents the location from being a top level location. Good for defining invisible structure.')
    objects = models.Manager()
    top_level = TopLevelManager()
 
    def children(self):
        """
        Returns all children that belong to this location one level deep. 
        Hidden children are ignored.
        """
        return self.location_set.filter(hidden=False)

    def root(self):
        """
        Returns this location's top-most parent location that isn't hidden.
        """
        root_location = self
        if self.parent:
            current = self
            last_visible = current
            while current.parent:
                current = current.parent
                if not current.hidden:
                    last_visible = current
            root_location = last_visible
        return root_location
 
    def get_absolute_url(self):
        return self.target_url

    def __unicode__(self):
        return self.name
 
    class Meta:
        ordering = ['order', 'id',]

