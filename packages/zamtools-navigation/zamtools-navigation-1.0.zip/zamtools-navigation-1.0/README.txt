Zamtools-navigation is a simple Django application that can be used to display 
navigation locations, as well as track the current location the user is at.

Locations can be nested under one another to produce a hierarchical layout of 
the site map. Additionally, the location structure does not need to follow the 
same structure of the urls.py, allowing off-site urls to be easily integrated 
and tracked. Certain locations can also be hidden, allowing them to act as 
structure to the hierarchy without being tracked by the current location.

Benefits

    * Hierarchical representation with methods for navigating children, root 
      and top_level locations
    * Explicit declaration of base and target urls allows for off-site 
      locations to be integrated into the hierarchy
    * Track the {{ top_locations }} and {{ current_location }} locations using 
      variables supplied by the context processors
    * Locations can be hidden, allowing them to act as structure in the 
      hierarchy, without being tracked by the current location
    * Locations can be put in any order. By default they sort by the order 
      they were added
    * Tests included 

Installation

Add zamtools-navigation to your project directory or put it somewhere on the 
PYTHONPATH.

You can also use easy_install:

> easy_install zamtools-navigation

In your settings.py file, add zamtools-navigation to the INSTALLED_APPS.

INSTALLED_APPS = (
   'navigation',
)

Add the top_level and current context processors to your 
TEMPLATE_CONTEXT_PROCESSORS.

TEMPLATE_CONTEXT_PROCESSORS = (
    'navigation.context_processors.top_level',
    'navigation.context_processors.current',
)

Synchronize your database.

> python manage.py syncdb

Usage

Log in to the Admin panel and create some locations.

It is usually a good idea to surround the base_url and target_url with slashes 
(eg: /about/) to prevent any ambiguity when urls are similar (eg: /about and 
/blog/about-last-night).

Locations that don't specify a parent are considered to be "top level" 
locations.

NOTE: It is not recommended that you create a root location, this will break 
top level functionality since that root would be the only top level location.

By default, the order the locations are displayed in are the order they were 
added. However, order can be more tightly controlled by using the order field. 
Locations are sorted in ascending order, with lower values being listed first.

Hidden locations are ignored by all Location model methods (top_level, root, 
children) and context processors (top_level, current). The purpose of hidden 
locations is to act as structure in the location hierarchy, but avoid being 
tracked as the current location.

Examples of hidden locations are /login/ and /logout/ pages that belong to an 
/accounts/ parent. The login and logout locations can be set to hidden, causing 
the current location detection to fall back on the accounts parent.
Context Variables

The zamtools-navigation context processors add top_locations and 
current_location variables to the context.

top_locations is a list of all locations without parents that aren't hidden.

current_location is the location that most closely matches the current url. If 
no match is found, its value is None.

The following is typically how you'd generate a menu with highlighting on the 
current location.

<ul class="navigation">
{% for location in top_locations %}
    <li id="navigation-{{ location.slug }}" {% ifequal location current_location %}class="navigation-current"{% endifequal %}>
        <a href="{{ location.target_url }}" title="{{ location.name }}">{{ location.name }}</a>
    </li>
{% endfor %}
</ul>

Testing

Tests can be performed using the standard Django test command.

> python manage.py test navigation