# encoding: utf-8

'''better_flash
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2007'
__id__ = '$Id: better_flash.py 312 2007-02-24 16:24:13Z chris $'
__url__ = '$URL: https://www.psychofx.com/psychofx/svn/Projects/Websites/zoner/frontend/trunk/zoner/zoner/better_flash.py $'
__version__ = '1.0'


# ---- Imports ----

# - TurboGears/CherryPy Modules -
import cherrypy
import turbogears.util as tg_util


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
