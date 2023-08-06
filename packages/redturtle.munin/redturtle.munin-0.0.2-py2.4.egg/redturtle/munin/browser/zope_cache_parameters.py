from Products.Five.browser import BrowserView

class Munin(BrowserView):
    
    def update(self):        
        if self.request['HTTP_X_FORWARDED_FOR'] or self.request['REMOTE_ADDR'] != '127.0.0.1':
            return "This script can only be called from localhost"
    
        result = []
        maindb = self.context.restrictedTraverse('/Control_Panel/Database/main')        

        result.append("total_objs:%s" % float(maindb.database_size()))
        result.append("total_objs_memory:%s" % float(maindb.cache_length()))
        result.append("target_number:%s" % float(len(maindb.cache_detail_length()) * maindb.cache_size()))
        return '\n'.join(result)