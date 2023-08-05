from zope.interface import (Attribute, Interface, implements)
from zinspect import conforms
from zinspect import (MissingAttribute, MissingMethod, DoesNotProvide,
        DoesNotImplement, InterfaceError)

# an interface declaration
class IFoo(Interface):
    """Foo blah blah"""

    x = Attribute("""X blah blah""")

    def bar(q, r=None):
        """bar blah blah"""

# an implementation
# that is good and will pass our inspection
class GoodClass1:
    '''Some implementation of the IFoo interface'''
    implements(IFoo)

    def __init__(self):
        self.x = None

    def bar(self):
        print 'Hello'

# another good implementation that should pass
class GoodClass2:
    '''Some altyernative implementation of the IFoo interface'''
    implements(IFoo)

    x = 3

    def bar(self):
        print 'Hello Bar'

# another good implementation that should pass
class GoodClass3(object):
    '''Some altyernative implementation of the IFoo interface'''
    implements(IFoo)

    x = 3

    def bar(self):
        print 'Hello Bar'

# an implementation
# that is false and will be uncovered by our inspection :)
class BadClass1:
    ''''''
    implements(IFoo)

    def bar(self):
        print 'I only have the bar method but no x attribute'

# another false implementation that should be detected
class BadClass2:
    implements(IFoo)
    x = 5
    # we don't have a bar method

# another class that should fail the exams since it does
# not declare to implement anything
class BadClass3:
    x = 6

    def bar(self):
        print 'Everything is present but we do not declare to implement'

def test_obj_conform_1():
    '''
    we will validate that an object conforms to an interface
    '''
    good_c = GoodClass1()
    errors = False
    try:
        conforms(good_c, IFoo)
    except InterfaceError, args:
        print args
        errors = True

    assert errors == False, "This object should have validated"

def test_obj_conform_2():
    good_c2 = GoodClass2()
    errors = False
    try:
        conforms(good_c2, IFoo)
    except InterfaceError, args:
        print args
        errors = True

    assert errors == False, "This object should have validated"

def test_class_conform_1():
    '''
    we will validate that a class conforms to an interface
    '''
    errors = False
    try:
        conforms(GoodClass1, IFoo)
    except InterfaceError, args:
        print args
        errors = True

    assert errors == False, "This class should have validated"

def test_class_conform_2():
    errors = False
    try:
        conforms(GoodClass2, IFoo)
    except InterfaceError, args:
        print args
        errors = True

    assert errors == False, 'This class should have validated'

def test_class_conform_3():
    errors = False
    try:
        conforms(GoodClass3, IFoo)
    except InterfaceError, args:
        print args
        errors = True

    assert errors == False, 'This new style class should have validated'

def test_obj_not_conform_1():
    '''
    we will validate that an object does not conform to an interface
    '''
    bad_c = BadClass1()
    errors = False
    try:
        conforms(bad_c, IFoo)
    except MissingAttribute, args:
        print args
        errors = True

    assert errors == True, \
            "This object should not validate since it misses an attribute"

def test_obj_not_conform_2():
    bad_c2 = BadClass2()
    errors = False
    try:
        conforms(bad_c2, IFoo)
    except MissingMethod, args:
        print args
        errors = True

    assert errors == True, \
            "This object should not validate since it misses a Method"

def test_class_not_conform_1():
    '''
    we will validate that a class does not conform to an interface
    '''
    errors = False
    try:
        conforms(BadClass1, IFoo)
    except MissingAttribute, args:
        print args
        errors = True

    assert errors == True, \
            "This class should not validate since it misses an attribute"

def test_class_not_conform_2():
    errors = False
    try:
        conforms(BadClass2, IFoo)
    except MissingMethod, args:
        print args
        errors = True

    assert errors == True, \
            "This class should not validate since it misses a method"

def test_obj_not_conform_3():
    '''
    we will validate that an object does not conform to an interface
    '''
    bad_c3 = BadClass3()
    errors = False
    try:
        conforms(bad_c3, IFoo)
    except DoesNotProvide, args:
        print args
        errors = True

    msg = "This object should not validate since it does"
    msg += " not declare to provide the required interface"

    assert errors == True, msg

def test_class_not_conform_3():
    '''
    we will validate that a class does not conform to an interface
    '''
    errors = False
    try:
        conforms(BadClass3, IFoo)
    except DoesNotImplement, args:
        print args
        errors = True

    msg = "This class should not validate since it does not"
    msg += "declare to implement the required interface"
    assert errors == True, msg

