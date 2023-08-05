import zope.component as capi
from interfaces import IAzaxPlugin
from zope.interface import implements
# concatresource is an embedded product 
import _concatresource
from concatresource.interfaces import IConcatResourceAddon
from json import getJsonAddonFiles
import zope.component as capi

class AzaxConcatResourceAddon(object):
    implements(IConcatResourceAddon)
    
    def getAddonFiles(self):
        try:
            files = self._addon_files
        except AttributeError:
            # Lazy setup of addon files
            self._addon_files = files = getJsonAddonFiles()
            # Lookup all utilities and add up the files from it
            plugins = capi.getAllUtilitiesRegisteredFor(IAzaxPlugin)
            for plugin in plugins:
                if plugin.jsfile and plugin.jsfile not in files:
                    files.append(plugin.jsfile)
        return files

azaxConcatResourceAddon = AzaxConcatResourceAddon()
