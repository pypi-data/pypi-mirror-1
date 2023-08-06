from zope.interface import Interface

class IMuninPlugin(Interface):
    """ Interface for zope munin plugins """
    
    def update_plugin(self):
        """ Return values for munin update """