# encoding: utf-8

'''breadcrumb_widget
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2007'
__id__ = '$Id: breadcrumb_widget.py 297 2007-02-19 16:18:08Z chris $'
__url__ = '$URL: https://www.psychofx.com/psychofx/svn/Projects/Websites/zoner/frontend/trunk/zoner/zoner/breadcrumb_widget.py $'
__version__ = '1.0'


# ---- Imports ----

# - Python Modules -

# - TurboGears Modules -
from turbogears import widgets


# ---- Classes ----

class BreadcrumbWidget(widgets.Widget):
    template = """
<div class="breadcrumb_trail" xmlns:py="http://purl.org/kid/ns#">
  <span py:for="i,crumb in enumerate(trail)" py:strip=""><span py:if="i > 0" py:content="separator" py:strip="" /><a py:if="crumb['href']" href="${crumb['href']}" py:content="crumb['text']" /><span py:if="not crumb['href']" py:replace="crumb['text']" /></span>
</div>
    """
    params = ["trail", "separator"]
    trail = []      # list of dicts {'text': 'crumb text', 'href': 'crumb link'}
    separator = u' -> '



