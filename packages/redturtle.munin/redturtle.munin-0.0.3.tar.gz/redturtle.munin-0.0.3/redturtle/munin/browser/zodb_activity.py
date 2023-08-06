from Products.Five.browser import BrowserView
from redturtle.munin.interfaces import IMuninPlugin
from time import time
from zope.interface import implements

class ZODBActivity(BrowserView):
    
    implements(IMuninPlugin, )
    
    def update(self):        
        if self.request['HTTP_X_FORWARDED_FOR'] or self.request['REMOTE_ADDR'] != '127.0.0.1':
            return "This script can only be called from localhost"
    
        result = []

        now = time()
        start =  now - 600
        end = now
                
        maindb = self.context.restrictedTraverse('/Control_Panel/Database/main')
        params = dict(chart_start=start,
                      chart_end=end)
        chart = maindb.getActivityChartData(200, params)        

        result.append("total_load_count:%s" % float(chart['total_load_count']))
        result.append("total_store_count:%s" % float(chart['total_store_count']))
        result.append("total_connections:%s" % float(chart['total_connections']))
        return '\n'.join(result)