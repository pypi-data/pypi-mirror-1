from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter, queryMultiAdapter
from redturtle.munin.interfaces import IMuninPlugin

class Munin(BrowserView):
    
    def update(self):
        """
        Get plugin name from request and try to get it from browser_view
        
        @author: Andrew Mleczko
        """        
        plugin_name = self.request.get('munin_plugin', None)
        if plugin_name:            
            plugin_view = queryMultiAdapter((self.context, self.request), name=plugin_name)
            if plugin_view:
                return plugin_view.update()