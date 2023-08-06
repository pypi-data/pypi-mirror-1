# encoding: utf-8

'''\
TGPriFlash is a TurboGears flash implementation that supports multiple
priority levels.

Out of the box, 3 levels are defined (FLASH_INFO, FLASH_WARNING,
FLASH_ALERT) but you can ignore these and use any integer values
you like as the flash priority levels.

To "magically" replace (aka monkey patch) turbogears.flash() with
this one, just add this import to your start-project.py::

    import tg_pri_flash.flash

Within your project you can import turbogears.flash as normal::

    from turbogears import flash

You'll want to replace the tg_flash line in your master template::

    <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>
  
with something like this::

    <div py:if="tg_flash and tg_flash[1]==0" class="flash_ok" py:content="tg_flash[0]"></div>
    <div py:if="tg_flash and tg_flash[1]==1" class="flash_warning" py:content="tg_flash[0]"></div>
    <div py:if="tg_flash and tg_flash[1]==2" class="flash_alert" py:content="tg_flash[0]"></div>

You would then define CSS definitions for each of the classes.

In your controller you can call flash() with a second argument, a positive integer::

    flash( _(u"There was an error"), 2 )

or, using the built-in constants::

    from tg_pri_flash.flash import FLASH_ALERT
    flash( _(u"There was an error"), FLASH_ALERT )

'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2007. All rights reserved.'
__id__ = '$Id: flash.py 829 2008-08-01 05:27:48Z chris $'
__url__ = '$URL: https://hugo.thoh.net/svn/psychofx/Projects/Python/TurboGears/TGPriFlash/trunk/tg_pri_flash/flash.py $'


# ---- Imports ----

# - TurboGears/CherryPy Modules -
import cherrypy
import turbogears.util as tg_util


# ---- Constants ----

FLASH_INFO = 0
FLASH_WARNING = 1
FLASH_ALERT = 2


# ---- Classes ----

def flash(message, priority=0):
    """Set a message to be displayed in the browser on next page display.
    Accepts an optional priority value, which should be a positive integer.
    """
    cherrypy.response.simple_cookie['tg_flash'] = tg_util.to_utf8(message)
    cherrypy.response.simple_cookie['tg_flash']['path'] = '/'
    if priority > 0:
        cherrypy.response.simple_cookie['tg_flash_pri'] = tg_util.to_utf8(str(priority))
        cherrypy.response.simple_cookie['tg_flash_pri']['path'] = '/'


def _get_flash():
    """Retrieve the flash message (if one is set), clearing the message."""
    priority = 0
    request_cookie = cherrypy.request.simple_cookie
    response_cookie = cherrypy.response.simple_cookie
    
    def clearcookie():
        response_cookie["tg_flash"] = ""
        response_cookie["tg_flash"]['expires'] = 0
        response_cookie['tg_flash']['path'] = '/'
        response_cookie["tg_flash_pri"] = ""
        response_cookie["tg_flash_pri"]['expires'] = 0
        response_cookie['tg_flash_pri']['path'] = '/'
    
    if response_cookie.has_key("tg_flash"):
        message = response_cookie["tg_flash"].value
        response_cookie.pop("tg_flash")
        if response_cookie.has_key("tg_flash_pri"):
            priority = response_cookie["tg_flash_pri"].value
            response_cookie.pop("tg_flash_pri")
        if request_cookie.has_key("tg_flash"):
            # New flash overrided old one sitting in cookie. Clear that old cookie.
            clearcookie()
    elif request_cookie.has_key("tg_flash"):
        message = request_cookie["tg_flash"].value
        if request_cookie.has_key("tg_flash_pri"):
            priority = request_cookie["tg_flash_pri"].value
        if not response_cookie.has_key("tg_flash"):
            clearcookie()
    else:
        message = None
    if priority is not None:
        try:
            priority = int(priority)
        except ValueError:
            priority = 0
    if message:
        message = unicode(message, 'utf-8')
        return (message, priority)
    else:
        return None


# Replace tg_flash with my preferred implementation
import turbogears
turbogears.flash = flash
if hasattr(turbogears.controllers, 'flash') and callable(turbogears.controllers.flash):
    turbogears.controllers.flash = flash
turbogears.controllers._get_flash = _get_flash
