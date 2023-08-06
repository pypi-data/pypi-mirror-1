"""
UML model support functions.

Functions collected in this module allow to

- create more complex UML model structures
- perform specific searches and manipulations

"""

import itertools
from gaphor.UML.uml2 import *

# '<<%s>>'
STEREOTYPE_FMT = '\xc2\xab%s\xc2\xbb'

def stereotypes_str(element, stereotypes=()):
    """
    Identify stereotypes of an UML metamodel instance and return coma
    separated stereotypes as string.

    :Parameters:
     element
        Element having stereotypes, can be None.
     stereotypes
        List of additional stereotypes, can be empty.
    """
    # generate string with stereotype names separated by coma
    if element:
        applied = (stereotype_name(st) for st in get_applied_stereotypes(element))
    else:
        applied = ()
    s = ', '.join(itertools.chain(stereotypes, applied))
    if s:
        return STEREOTYPE_FMT % s
    else:
        return ''


def stereotype_name(stereotype):
    """
    Return stereotype name suggested by UML specification. First will be
    character lowercase unless the second character is uppercase.

    :Parameters:
     stereotype
        Stereotype UML metamodel instance.
    """
    name = stereotype.name
    if not name:
        return ''
    elif len(name) > 1 and name[1].isupper():
        return name
    else:
        return name[0].lower() + name[1:]


def apply_stereotype(factory, element, stereotype):
    """
    Apply a stereotype to an element.

    :Parameters:
     factory
        UML metamodel factory.
     element
        UML metamodel class instance.
     stereotype
        UML metamodel stereotype instance.
    """
    obj = factory.create(InstanceSpecification)
    obj.classifier = stereotype
    element.appliedStereotype = obj
    return obj


def remove_stereotype(element, stereotype):
    """
    Remove a stereotype from an element.

    :Parameters:
     element
        UML metamodel element instance.
     stereotype
        UML metamodel stereotype instance.
    """
    for obj in element.appliedStereotype:
        if obj.classifier[0] is stereotype:
            del element.appliedStereotype[obj]
            obj.unlink()
            break


def get_stereotypes(factory, element):
    """
    Get sorted collection of possible stereotypes for specified element.
    """
    # UML specs does not allow to extend stereotypes with stereotypes
    if isinstance(element, Stereotype):
        return ()

    cls = type(element)

    # find out names of classes, which are superclasses of element class
    names = set(c.__name__ for c in cls.__mro__ if issubclass(c, Element))

    # find stereotypes that extend element class
    classes = factory.select(lambda e: e.isKindOf(Class) and e.name in names)
    
    stereotypes = set(ext.ownedEnd.type for cls in classes for ext in cls.extension)
    return sorted(stereotypes, key=lambda st: st.name)


def get_applied_stereotypes(element):
    """
    Get collection of applied stereotypes to an element.
    """
    return (obj.classifier[0] for obj in element.appliedStereotype)


def extend_with_stereotype(factory, element, stereotype):
    """
    Extend an element with a stereotype.
    """
    ext = factory.create(Extension)
    p = factory.create(Property)
    ext_end = factory.create(ExtensionEnd)

    ext.memberEnd = p
    ext.memberEnd = ext_end
    ext.ownedEnd = ext_end
    ext_end.type = stereotype
    ext_end.aggregation = 'composite'
    p.type = element
    p.name = 'baseClass'
    stereotype.ownedAttribute = p

    assert ext in element.extension

    return ext


def add_slot(factory, obj, attr):
    """
    Add slot to instance specification for an attribute.
    """
    slot = factory.create(Slot)
    slot.definingFeature = attr
    slot.value = factory.create(LiteralSpecification)
    obj.slot = slot
    return slot


# vim:sw=4:et
