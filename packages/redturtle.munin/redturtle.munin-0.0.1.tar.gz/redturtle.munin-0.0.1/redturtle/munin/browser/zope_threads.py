from Products.Five.browser import BrowserView
from ZServer.PubCore.ZRendezvous import ZRendevous
import thread
import threadframe

class Munin(BrowserView):
    
    def update(self):        
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