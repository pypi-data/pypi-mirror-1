from models import *
import re

def top_level(request):
    """
    Returns all top level locations; locations without a parent.
    """
    top_locations = Location.top_level.all()
    return {"top_locations": top_locations}

def current(request):
    """
    Returns the current location based on the url.
    """
    current_location = None
    full_path = request.get_full_path()

    # start at the end of the string
    i = len(full_path)
    while i > 0:
        # travel backwards along the string finding progressively smaller 
        # substrings between slashes until one is found in the database
        i = full_path.rfind('/', 0, i)
        locations = Location.objects.filter(base_url__iexact=full_path[0:i+1], hidden=False)
        if locations:
            current_location = locations[0]
            break
    return {"current_location": current_location}