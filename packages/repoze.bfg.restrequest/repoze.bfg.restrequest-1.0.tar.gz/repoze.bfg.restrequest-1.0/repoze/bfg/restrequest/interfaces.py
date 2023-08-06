from repoze.bfg.interfaces import IResponse, INewRequest, IRequest

class IPOSTRequest(IRequest):
    """marker interface for POST requests"""

class IGETRequest(IRequest):
    """marker interface for GET requests"""

class IPUTRequest(IRequest):
    """marker interface for PUT requests"""

class IDELETERequest(IRequest):
    """marker interface for DELETE requests"""



