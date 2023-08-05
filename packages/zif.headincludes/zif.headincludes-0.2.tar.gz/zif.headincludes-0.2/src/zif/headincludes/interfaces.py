from zope.interface import Interface

class IHeadIncludeRegistration(Interface):
    """registration for including a url appropriately in the head of an
       html document"""
    def register(url):
        """register the url for inclusion"""