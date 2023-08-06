"""BannerTool's main class"""

# Zope stuff
from Globals import InitializeClass 
from persistent.list import PersistentList
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem

# CMF stuff
from Products.CMFCore.permissions import View, ManagePortal
from Products.CMFCore.utils import UniqueObject


class BannerTool(UniqueObject, SimpleItem): 
    """
        Tool for managing viewlets to display banner images.
    """

    id = 'banner_tool'
    meta_type = 'Banner Tool'
    
    security = ClassSecurityInfo()

    def _getRegistry(self):
        "return the internal registry; creates it if non-existent"
        try:
            return self._registry
        except AttributeError:
            self._registry = PersistentList([])
            return self._registry

    def _register(self, data):
        """data is a dict holding the info needed like 
        'path', 'viewlet_id', 'image', 'text' """
        registry = self._getRegistry()
        registry.append(data.copy())
        
    def _clearRegistry(self):
        self._registry = PersistentList([])

    def _validate(self, item):
        # TODO: add validation; for now just return the item
        return item
   
    security.declareProtected(ManagePortal, 'setRegistry')
    def setRegistry(self, form_data):
        """clearing and populating the registry using the form input"""
        self._clearRegistry()
        for item in form_data:
            data = self._validate(item)
            self._register(data)

    security.declareProtected(ManagePortal, 'manage_setRegistry')
    def manage_setRegistry(self, request):
        """setting the registry from data recieved through a form"""
        data = request.form.copy()
        settings = data.get('settings', None)
        setting = data.get('setting', None)
        if settings is not None:
            self.setRegistry(settings)
        if setting is not None:
            self._register(setting)

    security.declareProtected(ManagePortal, 'manage_setRegistry')
    def manage_deleteSettings(self, request):
        """deleting selected settings from the registry

        Also needs the full settings in the request as it
        does also save eventual changes of settings that are kept"""
        data = request.form.copy()
        indices = data.get('indices', None)
        settings = data.get('settings', None)
        new = []
        for index in range(len(self.getSettings())):
            if index not in indices:
                new.append(settings[index])
        self.setRegistry(new)
        

    security.declareProtected(View, 'queryRegistry')
    def queryRegistry(self, query_string, key='path'):
        """returns a list of all items where 'query_string' matches
        the value stored under 'key' (defaulting to 'path')
        Individule viewlets need to check for themselves whether
        the item applies to them."""
        result = []
        for item in self._getRegistry():
            if item.get(key, None) == query_string:
                result.append(item.copy())
        return result

    security.declareProtected(View, 'getSettings')
    def getSettings(self):
        """return the entire registry (for the configuration UI)"""
        return list(self._getRegistry())
     
    
InitializeClass(BannerTool)
