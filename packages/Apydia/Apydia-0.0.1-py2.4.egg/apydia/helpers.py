"""
    Some helper functions used inside the templates
"""

from pprint import pformat


def is_included(pathname, options):
    """ Check if a pathname is to be included in the documentation """
    
    modules = options.modules
    exclude_modules = options.exclude_modules
    
    # Does the path match any of the excluded pattern?
    for m in exclude_modules:
        if pathname.startswith(m):
            return False

    # Are there any module patterns that match?
    if not [True for m in modules if pathname.startswith(m)]:
        return False
    
    return True
