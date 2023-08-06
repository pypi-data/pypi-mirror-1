from Products.Five.browser import BrowserView
from ZServer.PubCore.ZRendezvous import ZRendevous
from time import time
import thread
import threadframe

class Munin(BrowserView):
    
    def zodbactivity(self):
        """ """
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
    
    def zopecache(self):
        """ """
        if self.request['HTTP_X_FORWARDED_FOR'] or self.request['REMOTE_ADDR'] != '127.0.0.1':
            return "This script can only be called from localhost"
    
        result = []
        maindb = self.context.restrictedTraverse('/Control_Panel/Database/main')        

        result.append("total_objs:%s" % float(maindb.database_size()))
        result.append("total_objs_memory:%s" % float(maindb.cache_length()))
        result.append("target_number:%s" % float(len(maindb.cache_detail_length()) * maindb.cache_size()))
        return '\n'.join(result)
        
    def zopethreads(self):
        """ """
        if self.request['HTTP_X_FORWARDED_FOR'] or self.request['REMOTE_ADDR'] != '127.0.0.1':
            return "This script can only be called from localhost"
    
        result = []

        frames = threadframe.dict()
        total_threads = len(frames.values())
        free_threads = 0
        
        for frame in frames.values():
            _self =  frame.f_locals.get('self')
            if hasattr(_self, '__module__') and _self.__module__ == ZRendevous.__module__:
                free_threads += 1

        result.append("total_threads:%s" % float(total_threads))
        result.append("free_threads:%s" % float(free_threads))

        return '\n'.join(result)