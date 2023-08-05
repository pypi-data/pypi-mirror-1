# changed for using wsgi headincludes filter 7may06 jmw
# using utility 12may06 jmw

from zope.component import getUtility
from interfaces import IHeadIncludeRegistration

library_info = {}

class LibraryInfo(object):
    def __init__(self):
        self.included = []
        self.required = []


def need(library_name):
    registrar = getUtility(IHeadIncludeRegistration)
    if registrar:
        myList = [library_name]
        try:
            required = getRequired(library_name)
        except KeyError:
            raise RuntimeError('Unknown resource library: %s' % library_name)
        for lib in required:
            myList.append(lib)
        myList.reverse()
        for lib in myList:
            included = getIncluded(lib)
            for file_name in included:
                url = '/@@/%s/%s' % (library_name,file_name)
                registrar.register(url)

def getRequired(name):
    return library_info[name].required

def getIncluded(name):
    return library_info[name].included
