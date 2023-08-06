"""
Adapters
"""

from zope import interface, component

from gaphas.item import NW, SE
from gaphas import geometry
from gaphas import constraint
from gaphor import UML
from gaphor.core import inject
from gaphor.UML.umllex import render_attribute
from gaphor.diagram.interfaces import IEditor
from gaphor.diagram import items
from gaphor.misc.rattr import rgetattr, rsetattr


class CommentItemEditor(object):
    """
    Text edit support for Comment item.
    """
    interface.implements(IEditor)
    component.adapts(items.CommentItem)

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        return self._item.subject.body

    def get_bounds(self):
        return None

    def update_text(self, text):
        self._item.subject.body = text

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(CommentItemEditor)


class NamedItemEditor(object):
    """
    Text edit support for Named items.
    """
    interface.implements(IEditor)
    component.adapts(items.NamedItem)

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        return self._item.subject.name

    def get_bounds(self):
        return None

    def update_text(self, text):
        self._item.subject.name = text
        self._item.request_update()

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(NamedItemEditor)


class DiagramItemTextEditor(object):
    """
    Text edit support for diagram items containing text elements.
    """
    interface.implements(IEditor)
    component.adapts(items.DiagramItem)

    def __init__(self, item):
        self._item = item
        self._text_element = None

    def is_editable(self, x, y):
        if not self._item.subject:
            return False

        for txt in self._item.texts():
            if (x, y) in txt.bounds:
                self._text_element = txt
                break
        return self._text_element is not None

    def get_text(self):
        if self._text_element:
            return rgetattr(self._item.subject, self._text_element.attr)

    def get_bounds(self):
        return None

    def update_text(self, text):
        if self._text_element:
            self._text_element.text = text
            rsetattr(self._item.subject, self._text_element.attr, text)

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(DiagramItemTextEditor)


class ClassifierItemEditor(object):
    """
    Text editor support for Classifiers. Also features contained in Classifiers'
    compartments are edited through this interface.
    """
    interface.implements(IEditor)
    component.adapts(items.ClassifierItem)

    def __init__(self, item):
        self._item = item
        self._edit = None

    def is_editable(self, x, y):
        """
        Find out what's located at point (x, y), is it in the
        name part or is it text in some compartment
        """
        self._edit = self._item.item_at(x, y)
        return bool(self._edit and self._edit.subject)

    def get_text(self):
        if hasattr(self._edit.subject, 'render'):
            return self._edit.subject.render()
        return self._edit.subject.name

    def get_bounds(self):
        return None

    def update_text(self, text):
        if hasattr(self._edit.subject, 'parse'):
            return self._edit.subject.parse(text)
        else:
            self._item.subject.name = text

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(ClassifierItemEditor)
 

class AssociationItemEditor(object):
    interface.implements(IEditor)
    component.adapts(items.AssociationItem)

    def __init__(self, item):
        self._item = item
        self._edit = None

    def is_editable(self, x, y):
        """Find out what's located at point (x, y), is it in the
        name part or is it text in some compartment
        """
        item = self._item
        if not item.subject:
            return False
        if item.head_end.point((x, y)) <= 0:
            self._edit = item.head_end
        elif item.tail_end.point((x, y)) <= 0:
            self._edit = item.tail_end
        else:
            self._edit = item
        return True

    def get_text(self):
        if self._edit is self._item:
            return self._edit.subject.name
        return render_attribute(self._edit.subject)

    def get_bounds(self):
        return None

    def update_text(self, text):
        if hasattr(self._edit.subject, 'parse'):
            return self._edit.subject.parse(text)
        else:
            self._item.subject.name = text

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(AssociationItemEditor)
    


class ForkNodeItemEditor(object):
    """Text edit support for fork node join specification.
    """
    interface.implements(IEditor)
    component.adapts(items.ForkNodeItem)

    element_factory = inject('element_factory')

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        """
        Get join specification text.
        """
        if self._item.subject.joinSpec:
            return self._item.subject.joinSpec.value
        else:
            return ''

    def get_bounds(self):
        return None

    def update_text(self, text):
        """
        Set join specification text.
        """
        spec = self._item.subject.joinSpec
        if not spec:
            spec = self._item.subject.joinSpec = self.element_factory.create(UML.LiteralSpecification)
            spec.value = text

    def key_pressed(self, pos, key):
        pass

component.provideAdapter(ForkNodeItemEditor)

# vim:sw=4:et:ai
