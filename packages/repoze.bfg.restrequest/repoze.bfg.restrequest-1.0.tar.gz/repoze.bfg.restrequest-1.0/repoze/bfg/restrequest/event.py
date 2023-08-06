from zope.interface import alsoProvides

from interfaces import *


def handle_new_request(event):
    """attach a new interface to the request depending on the method
    
    This event handler will be called from repoze.bfg whenever a new
    request is created (INewRequest). See 
    
    http://static.repoze.org/bfgdocs/narr/events.html
    
    for more information.
    
    """
    req = event.request
    if req.method=="GET":
        alsoProvides(event.request, IGETRequest)
    elif req.method=="POST":
        alsoProvides(event.request, IPOSTRequest)
    elif req.method=="PUT":
        alsoProvides(event.request, IPUTRequest)
    elif req.method=="DELETE":
        alsoProvides(event.request, IDELETERequest)
