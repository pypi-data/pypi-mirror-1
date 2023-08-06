# vim: set expandtab ts=4 sw=4 filetype=python:

"""
Some twill-related nonsense.
"""

import inspect

from twill.errors import TwillAssertionError
from twill.commands import *
from BeautifulSoup import BeautifulSoup

LUDICROUSLY_NESTED = 3 

def img_has_alt():
    "Verify every img tag has an alt attribute."

    page_guts = get_browser().get_html()
    x = BeautifulSoup(page_guts)

    for img_tag in x.findAll('img'):
        if not [x for x in img_tag.attrs if x[0] == 'alt']:
            raise TwillAssertionError("No alt attribute in %s." % img_tag)

def no_nested_tables():
    "Verify no table has a table inside."

    page_guts = get_browser().get_html()
    x = BeautifulSoup(page_guts)

    for t in x.findAll('table'):
        if t.find('table'):
            raise TwillAssertionError(
                "1998 called and it wants its web design back.")

def run_on_page_load(funcname):
    "Run the function named funcname on every page load."
    
    try:
        f = globals()[funcname]
    except KeyError:
        parent_frame = inspect.currentframe(1)
        f = parent_frame.f_locals[funcname]

    # Now make a new function that discards the args passed in.
    def g(*args, **kwargs):
        return f()
    g.func_name = funcname
    
    # Add g to the post load hooks as long as it ain't already in there.
    b = get_browser()
    if not [x for x in b._post_load_hooks if x.func_name == funcname]:
        b._post_load_hooks.append(g)

def show_if_500():
    "Dump out the HTML for the page if it returns a 500."

    b = get_browser()
    if b.get_code() == 500:
        show()
        raise TwillAssertionError("Page %s returned a 500 status!" % b.get_url())

def complain_on_404():
    "Raise an exception if a page returns a 404."
    b = get_browser()
    if b.get_code() == 404:
        raise TwillAssertionError("Page %s returned a 404 status!" % b.get_url())

    
__id__ = "$Id: __init__.py 5 2008-02-25 19:31:51Z matt $"
