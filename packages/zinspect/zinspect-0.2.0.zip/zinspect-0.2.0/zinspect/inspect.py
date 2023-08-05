'''
the inspect module is used to inspect an object and make sure it conforms
to a specific interface declaration.
For this the object must declare that is implements the interface, but we
will also make sure the object really provides the attributes and methods
that the interface requires.
'''

import new
import zope.interface
from zope.interface import (Attribute, Interface, implements)
from zinspect import (MissingAttribute, MissingMethod,
        DoesNotProvide, DoesNotImplement)

__all__ = ['conforms']

# a class
reference_class = new.classobj('u', (), dict())
reference_newclass = new.classobj('u', (object,), dict())

# the type of a class
T_CLASS = type(reference_class)
T_NEWCLASS = type(reference_newclass)
# the type of an instance
T_INSTANCE = type(reference_class())

# create an anonymous method on an anonymous class
# this will be compared to make sure the objects and classes provide
# methods where they should
instance_method = new.instancemethod(
        lambda x: '',
        None,
        reference_class
        )

# the type of an instance method
T_INSTANCE_METHOD = type(instance_method)

def conforms(obj, interface):
    '''
    this function will inspect the given obj and return True if it conforms
    to the interface declaration interface given as the second argument.

    @param obj: an object to inspect, can be a class or an instance of a class
    @type obj: class or instance

    @param interface: an interface class that will be used to test if the
    given object is really implementing it
    @type obj: Interface Class
    '''
    assert type(interface) == type(Interface), \
            "interface must be of type zope.interface.Interface"

    if type(obj) == T_INSTANCE:
        if not interface.providedBy(obj):
            msg = "object %s does not declare to provide interface %s" % (
                    obj, interface)

            raise DoesNotProvide(msg)

    elif type(obj) == T_CLASS or type(obj) == T_NEWCLASS:
        if not interface.implementedBy(obj):
            msg = "class %s does not declare to implement interface %s" % (
                    obj, interface)

            raise DoesNotImplement(msg)

    else:
        msg = "Unknown type for obj: %s" % type(obj)
        raise TypeError(msg)

    # get all the attributes required by the interface
    inames = interface.names()

    for name in inames:
        missing_attrs = list()
        req_type = type(interface.get(name))

        try:
            # test if attribute is present
            req_attr = getattr(obj, name)

        except:
            msg = "%s does not contain the required attribute: %s" % (
                    obj, name) 
            # here we are missing the attr at the class level
            # we must now inspect the __init__ method
            missing_attrs.append(name)

        if req_type == zope.interface.interface.Method:
            # here we should test for attributes of type method
            # XXX TODO: we should also test for the method signature
            # which is possible with zope.interface
            # by looking into 
            # met = interface.get(name)
            # siginfo = met.getSignatureInfo()
            if not type(req_attr) == T_INSTANCE_METHOD:
                msg = "Attribute %s is not of the required type:"
                msg += "instancemethod"
                msg = msg % name
                raise MissingMethod(msg)

        try:
            # get the __init__ function
            f_init = obj.__dict__['__init__']
            # grab the code for this function
            init_code = f_init.func_code

            # and now inspect code
            for mattr in missing_attrs:
                if mattr in init_code.co_names:
                    # remove attr name since we found it in the
                    # __init__ method
                    missing_attrs.remove(mattr)
                else:
                    # TODO: find if some methods are called in the __init__
                    # method follow each of them and inspect each of them
                    # to find if our attribute is defined there
                    pass

        except KeyError:
            pass

        if len(missing_attrs) > 0:
            msg = "Missing attributes: %s" % missing_attrs
            raise MissingAttribute(msg)

    return True

