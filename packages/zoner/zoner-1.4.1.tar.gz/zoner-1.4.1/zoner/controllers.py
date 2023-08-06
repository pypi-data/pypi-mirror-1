# encoding: utf-8

'''controllers : for zoner
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2007'
__id__ = '$Id: controllers.py 816 2008-07-27 07:28:16Z chris $'
__url__ = '$URL: https://www.psychofx.com/psychofx/svn/Projects/Websites/zoner/frontend/trunk/zoner/zoner/controllers.py $'


# ---- Imports ----

# - Python Modules -
try:
    from elementtree import ElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET
import os
import shutil

# - TurboGears Modules -
from turbogears import config, controllers, expose
from turbogears import identity, redirect
from turbogears import widgets, validators, validate, error_handler
from turbogears import paginate
from turbogears.widgets import PaginateDataGrid
from cherrypy import request, response, HTTPRedirect
# from zoner import json
import logging
log = logging.getLogger("zoner.controllers")

# - Other Modules -
from easyzone import easyzone
from easyzone.zone_check import ZoneCheck
from easyzone.zone_reload import ZoneReload, ZoneReloadError
from tg_boolean_form_widget.tg_boolean_form_widget import BooleanForm

# - zoner modules -
from zoner.better_flash import flash
from zoner.expanding_form import expanding_form
from zoner.model import ChangeHistory, CHANGE_TYPE_SAVE, CHANGE_TYPE_RELOAD, CHANGE_TYPE_REVERT, CHANGE_TYPES
from zoner.release import version
from zoner.soa_form import soa_form


# ---- Constants ----

SUPPORTED_RECORD_TYPES = ('A', 'CNAME', 'MX', 'NS', 'TXT')

FLASH_INFO = 0
FLASH_WARNING = 1
FLASH_ALERT = 2


# ---- Widgets ----

# <tr py:for="change in history">
#   <td>${change.timestamp_format("%Y/%m/%d %H:%M:%S")}</td>
#   <td>${change.user_object().display_name} (${change.user_object().user_name})</td>
#   <td>${change.serial}</td>
#   <td><span py:if="change.change_type=='S'" py:replace="_(u'Modified')" /><span py:if="change.change_type=='R'" py:replace="_(u'Reloaded')" /><span py:if="change.change_type=='V'" py:replace="_(u'Reverted')" /></td>
#   <td>
#     <a py:if="change.archived_name" href="history_record?zone=${zonename}&amp;archive=${change.archived_name}">View</a>
#   </td>
# </tr>

def history_timestamp(obj):
    return obj.timestamp_format("%Y/%m/%d %H:%M:%S")

def history_user(obj):
    u = obj.user_object()
    return "%s (%s)" %(u.display_name, u.user_name)

CHANGE_DESC = {
    'S': _(u'Modified'),
    'R': _(u'Reloaded'),
    'V': _(u'Reverted')
}

def history_change_type(obj):
    return CHANGE_DESC.get(obj.change_type, '??')

def history_view(obj):
    if obj.archived_name:
        href = 'history_record?zone=%s&archive=%s' %(obj.zone, obj.archived_name)
        view = ET.Element('a', href=href, style='text-decoration: underline')
        view.text = u'View'
    else:
        view = u''
    return view
    

history_grid = PaginateDataGrid(
    name = 'history_grid',
    # template = 'zoner.templates.history_paginate_datagrid',
    fields=[
        PaginateDataGrid.Column(
                name = 'timestamp',
                getter = history_timestamp,
                title = 'Timestamp',
                options = dict(sortable=True)
        ),
        PaginateDataGrid.Column(
                name = 'user',
                getter = history_user,
                title = 'User',
                options = dict(sortable=True)
        ),
        PaginateDataGrid.Column(
                name = 'serial',
                getter = 'serial',
                title = 'Serial',
                options = dict(sortable=True)
        ),
        PaginateDataGrid.Column(
                name = 'change_type',
                getter = history_change_type,
                title = 'Type of Change',
                options = dict(sortable=True)
        ),
        PaginateDataGrid.Column(
                name = 'view',
                getter = history_view,
                title = '',
        ),
    ]
)



# ---- Helper Classes ----

class ManagedZones(object):
    def __init__(self, zonedir):
        self.zonedir = zonedir
        self.zonefiles = [f for f in os.listdir(zonedir) if len(f) > 2 and f[0] not in ('.', '_')]
    
    def __len__(self):
        return len(self.zonefiles)
    
    def __iter__(self):
        return iter(self.zonefiles)
    



# ---- Controllers ----

class ZoneController(controllers.Controller, identity.SecureResource):
    '''The controller for managing DNS zones.
    
    This whole controller is protected by identity.  Only an authorised user
    may access it.
    '''
    require = identity.not_anonymous()
    
    @expose(template=".templates.zones")
    def index(self):
        zonedir = config.get('zoner.zonedir')
        zones = ManagedZones(zonedir)
        return dict(
            zonecount = len(zones),
            zones = zones,
        )
    
    @expose(template=".templates.managezone")
    def manage(self, zone=None, auto_inc_serial=False):
        auto_inc_serial = bool(auto_inc_serial)
        
        z = get_zone(zone)
        
        hostnames = sorted_hostnames(zone, z.names.keys())
        
        rndc_path = config.get('zoner.rndc', None)
        if rndc_path is None:
            enable_refresh = False
        else:
            enable_refresh = True
        
        crumbtrail = [
            # Tuples of ('display text', href) where href is string or None
            dict( text=_(u'Home'), href='../' ),
            dict( text=_(u'Manage Zones'), href='./' ),
            dict( text=z.domain, href=None ),
        ]
        
        return dict(
            auto_inc_serial = auto_inc_serial,
            crumbtrail = crumbtrail,
            enable_refresh = enable_refresh,
            hostnames = hostnames,
            names = z.names,
            root = z.root,
            soa = z.root.soa,
            zonename = z.domain,
        )
    
    @expose(template=".templates.editsoa")
    def editsoa(self, zone=None):
        z = get_zone(zone)
        
        soa = z.root.soa
        
        crumbtrail = [
            # Tuples of ('display text', href) where href is string or None
            dict( text=_(u'Home'), href='../' ),
            dict( text=_(u'Manage Zones'), href='./' ),
            dict( text=z.domain, href='manage?zone=%s' %z.domain ),
            dict( text=_(u'Edit SOA'), href=None ),
        ]
        
        return dict(
            action = 'savesoa',
            crumbtrail = crumbtrail,
            options = {},
            soa_form = soa_form,
            submit_text = 'Save',
            value = dict(
                soa_fields = {
                    'zone' : z.domain,
                    'mname' : soa.mname,
                    'rname' : soa.rname,
                    'serial' : soa.serial,
                    'refresh' : soa.refresh,
                    'retry' : soa.retry,
                    'expire' : soa.expire,
                    'minttl' : soa.minttl,
                }
            ),
            zone = z.domain,
        )
    
    @expose()
    @validate(form=soa_form)
    @error_handler(editsoa)
    def savesoa(self, soa_fields, cancel=None):
        zone = soa_fields['zone']
        z = get_zone(zone)
        
        if cancel:
            flash( _(u'Changes cancelled.'), FLASH_WARNING )
            redirect("/zone/manage?zone=%s" % z.domain)
        
        soa = z.root.soa
        
        soa.mname = soa_fields['mname']
        soa.rname = soa_fields['rname']
        soa.refresh = soa_fields['refresh']
        soa.retry = soa_fields['retry']
        soa.expire = soa_fields['expire']
        soa.minttl = soa_fields['minttl']
        if soa.serial == soa_fields['serial']:
            auto_inc_serial = True
        else:
            auto_inc_serial = False
            soa.serial = soa_fields['serial']
        
        archive_file = archive_zone(z)
        archive_serial = z.root.soa.serial
        
        try:
            z.save(autoserial=auto_inc_serial)
        except Exception, e:
            flash( str(e), FLASH_ALERT )
            auto_inc_serial = False
        else:
            if not check_zone(z.domain, z.filename):
                flash( _(u"Zone was saved but failed syntax check. Please examine file: %s" %z.filename), FLASH_ALERT )
            else:
                flash( _(u"Updated SOA for %s") % z.domain, FLASH_INFO )
                audit_change(CHANGE_TYPE_SAVE, z.domain, archive_file, archive_serial, identity.current.user.user_id)
        
        redirect("/zone/manage?zone=%s&auto_inc_serial=%s" % (z.domain, int(auto_inc_serial)))
    
    @expose(template=".templates.editzone")
    def editzone(self, zone=None, tg_errors=None):
        z = get_zone(zone)
        hostnames = sorted_hostnames(zone, z.names.keys())
        
        values = dict(
            zone = zone,
            zones = [],
        )
        
        attrs = dict(
            zones = [],
        )
        
        for host in hostnames:
            for ntype in SUPPORTED_RECORD_TYPES:
                node = z.names[host].records(ntype)
                if node:
                    for record in node.items:
                        inputrow = dict(
                                hostname = host,
                                type = ntype,
                                value = record,
                                preference = '',
                        )
                        rowattrs = dict()
                        if ntype == 'MX':
                            inputrow['preference'] = record[0]
                            inputrow['value'] = record[1]
                        else:
                            rowattrs['preference'] = dict(style='visibility:hidden;', size=4)
                        values['zones'].append(inputrow)
                        attrs['zones'].append(rowattrs)
        
        if tg_errors:
            flash( _(u"There was a problem with the form!"), FLASH_ALERT )
        
        crumbtrail = [
            # Tuples of ('display text', href) where href is string or None
            dict( text=_(u'Home'), href='../' ),
            dict( text=_(u'Manage Zones'), href='./' ),
            dict( text=z.domain, href='manage?zone=%s' %z.domain ),
            dict( text=_(u'Edit Zone'), href=None ),
        ]
        
        return dict(
            action = 'savezone',
            crumbtrail = crumbtrail,
            form = expanding_form,
            options = {},
            attrs = attrs,
            submit_text = _(u'Save'),
            value = values,
            zonename = z.domain,
        )
    
    @expose()
    @validate(form=expanding_form)
    @error_handler(editzone)
    def savezone(self, zone=None, zones=None, cancel=None):
        
        # DEBUG:
        # print "zone:",zone
        # from pprint import pformat
        # print "zones:",pformat(zones)
        
        z = get_zone(zone)
        
        if cancel:
            flash( _(u'Changes cancelled.'), FLASH_WARNING )
            redirect("/zone/manage?zone=%s" % z.domain)
        
        save_ok = True
        auto_inc_serial = False
        
        # remove existing nodes
        names = z.names.keys()
        names.remove(z.domain)  # remove '@' (root)
        for name in names:
            z.delete_name(name)
        # delete nodes from '@' but don't remove it completely (otherwise SOA is gone...)
        root = z.root
        root.clear_all_records(exclude='SOA')
        
        # replace with values submitted from form
        for record in zones:
            hostname = record['hostname']
            rtype = record['type']
            preference = record['preference']
            value = record['value']
            
            if hostname and value and rtype in SUPPORTED_RECORD_TYPES:
                if hostname not in z.names.keys():
                    z.add_name(hostname)
                name = z.names[hostname]
                if rtype == 'MX':
                    name.records(rtype, create=True).add( (int(preference), str(value)) )
                else:
                    name.records(rtype, create=True).add(str(value))
            
            else:
                # TODO: re-display form with errors ?
                save_ok = False
                # flash('Some of the records were invalid', FLASH_ALERT)
                # return self.editzone(zone=zone)
        
        if save_ok:
            archive_file = archive_zone(z)
            archive_serial = z.root.soa.serial
            auto_inc_serial = True
            z.save(autoserial=auto_inc_serial)
            if not check_zone(z.domain, z.filename):
                flash( _(u"Zone was saved but failed syntax check. Please examine file: %s" %z.filename), FLASH_ALERT )
            else:
                flash( _(u"Zone %s has been saved. Don't forget to signal named to reload the zone.") % z.domain, FLASH_INFO )
                audit_change(CHANGE_TYPE_SAVE, z.domain, archive_file, archive_serial, identity.current.user.user_id)
        
        redirect("/zone/manage?zone=%s&auto_inc_serial=%s" % (z.domain, int(auto_inc_serial)))
    
    @expose()
    def reload(self, zone=None):
        z = get_zone(zone)
        
        if not check_zone(z.domain, z.filename):
            flash( _(u"Zone file failed syntax check, please examine: %s") %z.filename, FLASH_ALERT )
        
        else:
            rndc_path = config.get('zoner.rndc', None)
            if rndc_path is None:
                flash( _(u"Reload signalling is disabled. Set 'zoner.rndc' in the config to enable."), FLASH_WARNING )
            else:
                zr = ZoneReload(rndc=rndc_path)
                try:
                    zr.reload(z.domain)
                except ZoneReloadError, err:
                    flash( _(u"zone reload failed: %s") %err, FLASH_ALERT )
                else:
                    flash( _(u"named has been signalled to reload zone %s") %z.domain, FLASH_INFO )
                    audit_change(CHANGE_TYPE_RELOAD, z.domain, None, z.root.soa.serial, identity.current.user.user_id)
        
        redirect("/zone/manage?zone=%s" %z.domain)
    
    @expose(template='.templates.history')
    @paginate('history', default_order='-timestamp', limit=50, allow_limit_override=True)
    def history(self, zone=None):
        z = get_zone(zone)
        history = ChangeHistory.history_records(z.domain)
        
        crumbtrail = [
            # Tuples of ('display text', href) where href is string or None
            dict( text=_(u'Home'), href='../' ),
            dict( text=_(u'Manage Zones'), href='./' ),
            dict( text=z.domain, href='manage?zone=%s' %z.domain ),
            dict( text=_(u'Change History'), href=None ),
        ]
        
        return dict(
            crumbtrail = crumbtrail,
            grid = history_grid,
            history = history,
            zonename = zone,
        )
    
    @expose(template='.templates.history_record')
    def history_record(self, zone=None, archive=None):
        z = get_archive(zone, archive)
        
        hostnames = sorted_hostnames(archive, z.names.keys())
        
        crumbtrail = [
            # Tuples of ('display text', href) where href is string or None
            dict( text=_(u'Home'), href='../' ),
            dict( text=_(u'Manage Zones'), href='./' ),
            dict( text=z.domain, href='manage?zone=%s' %z.domain ),
            dict( text=_(u'Change History'), href="history?zone=%s" %z.domain ),
            dict( text=str(z.root.soa.serial), href=None )
        ]
        
        return dict(
            archivename = archive,
            crumbtrail = crumbtrail,
            hostnames = hostnames,
            names = z.names,
            root = z.root,
            soa = z.root.soa,
            zonename = z.domain,
        )
    
    @expose(template='.templates.revert')
    def revert(self, zone=None, archive=None):
        z = get_zone(zone)
        za = get_archive(zone, archive)
        
        crumbtrail = [
            # Tuples of ('display text', href) where href is string or None
            dict( text=_(u'Home'), href='../' ),
            dict( text=_(u'Manage Zones'), href='./' ),
            dict( text=z.domain, href='manage?zone=%s' %z.domain ),
            dict( text=_(u'Change History'), href="history?zone=%s" %z.domain ),
            dict( text=str(za.root.soa.serial), href="history_record?zone=%s&archive=%s" %(z.domain, archive) ),
            dict( text=_(u'Revert'), href=None ),
        ]
        
        return dict(
            action = 'confirm_revert',
            archived_zone = za,
            archivename = archive,
            crumbtrail = crumbtrail,
            form = BooleanForm(fields=[widgets.HiddenField('zone'), widgets.HiddenField('archive')]),
            no_text = 'Cancel',
            options = {},
            value = dict(
                    zone = z.domain,
                    archive = archive,
            ),
            yes_text = 'Confirm',
            zone = z,
            zonename = z.domain,
        )
    
    @expose()
    def confirm_revert(self, zone=None, archive=None, yes=None, no=None, cancel=None, confirm=None):
        if not yes:
            flash( _(u'Changes cancelled.'), FLASH_WARNING )
            redirect("/zone/history_record?zone=%s&archive=%s" % (zone, archive))
        
        z = get_zone(zone)
        za = get_archive(zone, archive)
        archive_serial = za.root.soa.serial
        
        archive_file = archive_zone(z)
        
        za.root.soa.serial = z.root.soa.serial
        za.save(filename=z.filename, autoserial=True)
        
        audit_change(CHANGE_TYPE_REVERT, za.domain, archive_file, z.root.soa.serial, identity.current.user.user_id)
        
        flash( _(u"Zone reverted back to serial %s") %archive_serial, FLASH_INFO )
        redirect("/zone/manage?zone=%s" %za.domain)
    



class Root(controllers.RootController):
    
    zone = ZoneController()
    
    @expose(template=".templates.welcome")
    def index(self):
        zonedir = config.get('zoner.zonedir')
        zones = ManagedZones(zonedir)
        return dict(
            zonecount = len(zones),
            zones = zones,
        )
    
    @expose(template='.templates.about')
    def about(self):
        crumbtrail = [
            # Tuples of ('display text', href) where href is string or None
            dict( text=_(u'Home'), href='./' ),
            dict( text=_(u'About'), href=None ),
        ]
        
        return dict(
            crumbtrail=crumbtrail,
            version=version,
        )
    
    @expose(template=".templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= request.path

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= request.headers.get("Referer", "/")
            
        response.status=403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=request.params,
                    forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")
        # raise HTTPRedirect(
        #     config.get('base_url_filter.base_url', '') +
        #     config.get('server.webpath', '') +
        #     '/'
        # )
    




# ---- Helper Functions ----

def get_zone(zonename):
    '''Return a Zone instance for zonename that has been loaded
    from the actual zone file.
    If the zone file cannot be found or loaded, a redirect to "/"
    is raised.
    '''
    if not zonename:
        flash( _(u"Not a valid zone!"), FLASH_ALERT )
        raise redirect("/")
        
    z = easyzone.Zone(zonename)
    zonedir = config.get('zoner.zonedir')
    zone_file = find_zone_file(zonedir, zonename)
    if not zone_file:
        flash( _(u"Not a valid zone!"), FLASH_ALERT )
        raise redirect("/")
    
    z.load_from_file(zone_file)
    return z


def get_archive(zonename, filename):
    '''Return a Zone instance for zonename that has been loaded
    from an archived zone file filename.
    If the zone file cannot be found or loaded, a redirect to "/"
    is raised.
    '''
    if not zonename:
        flash( _(u"Not a valid zone!"), FLASH_ALERT )
        raise redirect("/")
    
    z = easyzone.Zone(zonename)
    archive_dir = config.get('zoner.archive_dir', None)
    if archive_dir is None:
        flash( _(u"zoner.archive_dir configuration is not defined"), FLASH_ALERT )
        raise redirect("/")
    zone_file = find_zone_file(archive_dir, filename)
    if not zone_file:
        flash( _(u"Archived zone file does not exist"), FLASH_ALERT )
        raise redirect("/")
    
    z.load_from_file(zone_file)
    return z


def find_zone_file(zonedir, zonename):
    '''Find the zone file name by trying a few common
    extensions, including:
    * no extension ('example.com')
    * trailing dot ('example.com.')
    * .db ('example.com.db')
    * .zone ('example.com.zone')
    '''
    # remove any trailing dot
    if zonename[-1] == '.':
        zonename = zonename[:-1]
    
    extensions = ('', '.', '.db', 'zone')
    
    for ext in extensions:
        zone_file = os.path.join(zonedir, zonename + ext)
        if os.path.isfile(zone_file):
            return zone_file
    
    return None


def sorted_hostnames(zonename, hostnames):
    if zonename in hostnames:
        # sort hostnames but move root zone to start of list
        del hostnames[hostnames.index(zonename)]
        hostnames.sort()
        hostnames.insert(0, zonename)
    else:
        # sort hostnames
        hostnames.sort()
    
    return hostnames

def check_zone(zonename, zonefile):
    '''Check the syntax of a zonefile by calling the named-checkzone
    binary defined in the TurboGears config 'zoner.checkzone'.
    If 'zoner.checkzone' is not defined then this check is disabled
    (it always returns True).
    '''
    checkzone_path = config.get('zoner.checkzone', None)
    if checkzone_path is None:
        # skip the check
        return True
    
    c = ZoneCheck(checkzone_path)
    r = c.isValid(zonename, zonefile)
    if not r:
        log.warn("ZoneCheck failed for zone='%s' file='%s' error was: %s" %(zonename, zonefile, c.error))
    return r

def archive_zone(zone):
    '''Copies a zone file to the archive directory defined in config
    by "zoner.archive_dir".
    
    Returns the filename (not including path) of the archived file.
    
    If "zoner.archive_dir" is not defined then nothing will be archived
    and this function will return None.
    '''
    archive_dir = config.get('zoner.archive_dir', None)
    if archive_dir is None:
        return None
    
    filename = zone.domain + str(zone.root.soa.serial)
    
    full_path = os.path.join(archive_dir, filename)
    
    if os.path.exists(full_path):
        # this is an unusual situation
        raise Exception("archive_zone() failed as archived file already exists: %s" %full_path)
    
    shutil.copyfile(zone.filename, full_path)
    
    return filename

def audit_change(change_type, zone, filename, serial, user_id):
    assert change_type in CHANGE_TYPES
    change = ChangeHistory(zone=zone, user=user_id, serial=serial, change_type=change_type, archived_name=filename)

def register_widgets(widgets, pkg_name): 
     """Include site-wide widgets on every page. 

     'widgets' is a list of widget instance names. 

     Order of the widget names is important for proper inclusion 
     of JavaScript and CSS. 

     The named widget instances have to be instantiated in 
     some of your modules. 

     'pkg_name' is the name of your Python module/package, in which 
     the widget instances are defined. 
     """ 

     # first get widgets listed in the config files 
     include_widgets = config.get('tg.include_widgets', []) 
     # then append given list of widgets 
     for widget in widgets: 
         include_widgets.append('%s.%s' % (pkg_name, widget)) 
     config.update({'global': {'tg.include_widgets': include_widgets}}) 

_sitewidgets = [
   'BreadcrumbWidget',
] 

register_widgets(_sitewidgets, 'zoner.breadcrumb_widget') 
