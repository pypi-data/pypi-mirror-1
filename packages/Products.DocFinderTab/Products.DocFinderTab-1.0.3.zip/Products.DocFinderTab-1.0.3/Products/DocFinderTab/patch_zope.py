# DocFinderTab 1.0.3
# (c) 2001-2009, Stefan H. Holek, stefan@epy.co.at
# http://zope.org/Members/shh/DocFinderTab
# License: ZPL
# Zope: 2.7-2.12

# Monkey patch wrapper around Dieter Maurer's DocFinder product
# http://www.dieter.handshake.de/pyprojects/zope/DocFinder.html
# Adds a Doc tab to all Zope objects

# Thanks to Dieter for his input on how to make this work with
# PythonScripts and ExternalMethods, and for writing DocFinder
# in the first place.

__doc__ = 'Add a Doc tab to all Zope objects'
__version__ = '1.0.3'

__refresh_module__ = 0

try:

    from Globals import HTMLFile
    from App.Management import Tabs
    from OFS.SimpleItem import Item
    from analyse import Doc as DocFinder
    from AccessControl import getSecurityManager
    from AccessControl.PermissionRole import PermissionRole
    from permissions import ViewDocPermission, ViewDocDefaultRoles
    from logging import getLogger

    def filtered_manage_options(self, REQUEST=None):
        # Append a Doc tab to an object's management tabs
        tabs = self._old_filtered_manage_options(REQUEST)
        security = getSecurityManager()
        if len(tabs) and security.checkPermission(ViewDocPermission, self.this()):
            tabs.append( {'label': 'Doc',
                          'action': 'showDocumentation',
                          'help': ('DocFinderTab', 'README.stx')} )
        return tabs

    if not hasattr(Tabs, '_old_filtered_manage_options'):
        Tabs._old_filtered_manage_options = Tabs.filtered_manage_options
        Tabs.filtered_manage_options = filtered_manage_options

    showDocumentation = HTMLFile('dtml/showDocumentation', globals())

    def analyseDocumentation(self, object, type='scripter', filter=''):
        return DocFinder(object, type, filter)

    ViewDocRoles = PermissionRole(ViewDocPermission, ViewDocDefaultRoles)

    Item.showDocumentation = showDocumentation
    Item.showDocumentation__roles__ = ViewDocRoles
    Item.analyseDocumentation = analyseDocumentation
    Item.analyseDocumentation__roles__ = ViewDocRoles

    logger = getLogger('DocFinderTab')
    logger.info('Applied patch version %s.', __version__)

except:

    import traceback
    traceback.print_exc()

