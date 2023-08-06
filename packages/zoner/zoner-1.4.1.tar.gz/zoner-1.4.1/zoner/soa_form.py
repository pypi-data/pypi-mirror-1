# encoding: utf-8

'''soa_form
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2007'
__id__ = '$Id: soa_form.py 321 2007-03-04 23:32:37Z chris $'
__url__ = '$URL: https://www.psychofx.com/psychofx/svn/Projects/Websites/zoner/frontend/trunk/zoner/zoner/soa_form.py $'


# ---- Imports ----

# - TurboGears Modules -
from turbogears import widgets, validators


# ---- Widgets / Forms ----

class SOAFields(widgets.WidgetsList):
    mname = widgets.TextField('mname',
            label=_(u"MNAME"),
            help_text=_(u"Primary master server.")
    )
    
    rname = widgets.TextField('rname',
            label=_(u"RNAME"),
            help_text=_(u"Admin e-mail address.")
    )
    
    serial = widgets.TextField('serial',
            label=_(u"Serial"),
            help_text=_(u"Serial number of this zone.")
    )
    
    refresh = widgets.TextField('refresh',
            label=_(u"Refresh"),
            help_text=_(u"Refresh interval in seconds.")
    )
    
    retry = widgets.TextField('retry',
            label=_(u"Retry"),
            help_text=_(u"Retry interval in seconds.")
    )
    
    expire = widgets.TextField('expire',
            label=_(u"Expire"),
            help_text=_(u"Expire interval in seconds.")
    )
    
    minttl = widgets.TextField('minttl',
            label=_(u"Min TTL"),
            help_text=_(u"Minimum Time-To-Live in seconds.")
    )
    
    zone = widgets.HiddenField('zone',
    )



class SOASchema(validators.Schema):    
    mname = validators.UnicodeString(not_empty=True, max=256, strip=True)
    rname = validators.UnicodeString(not_empty=True, max=256, strip=True)
    serial = validators.Int(not_empty=True)
    refresh = validators.Int(not_empty=True)
    retry = validators.Int(not_empty=True)
    expire = validators.Int(not_empty=True)
    minttl = validators.Int(not_empty=True)
    zone = validators.UnicodeString(not_empty=True, max=256, strip=True)


class SOATableForm(widgets.TableForm):
    template = 'zoner.templates.soa_tabletemplate'


class FixedListForm(widgets.ListForm):
    template = 'zoner.templates.fixed_list_form'


cancel = widgets.SubmitButton(name='cancel', attrs=dict(value=_(u'Cancel')), label=_(u'Cancel all changes'))
soa_table_form = SOATableForm(name='soa_fields', fields=SOAFields(), validator=SOASchema() )
# soa_table_form = widgets.TableForm(name='soa_fields', fields=SOAFields(), validator=SOASchema() )

soa_form = FixedListForm(
    name='soaform',
    fields=[soa_table_form, cancel],
)
