'''
Theses are the exceptions that can be raised by this module
'''

class InterfaceError(Exception): pass
class MissingAttribute(InterfaceError): pass
class MissingMethod(InterfaceError): pass
class DoesNotProvide(InterfaceError): pass
class DoesNotImplement(InterfaceError): pass

