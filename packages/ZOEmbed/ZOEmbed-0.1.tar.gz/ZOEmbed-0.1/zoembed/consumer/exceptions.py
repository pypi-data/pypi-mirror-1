# -*- coding: utf-8 -*-

class OEmbedError(Exception):
    pass
    
class EndpointNotFound(OEmbedError):
    pass

class InvalidURLScheme(OEmbedError):
    pass

class InvalidResponse(OEmbedError):
    pass