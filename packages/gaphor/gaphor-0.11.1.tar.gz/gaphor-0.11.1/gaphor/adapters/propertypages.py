"""
Adapters for the Property Editor

# TODO: make all labels align top-left
# Add hidden columns for list stores where i can put the actual object
# being edited.

TODO:
 - stereotypes
 - association / association ends.
 - 
"""

import gtk
from gaphor.core import _, inject, transactional
from gaphor.ui.interfaces import IPropertyPage
from gaphor.diagram import items
from zope import interface, component
from gaphor import UML
from gaphor.UML.umllex import parse_attribute, render_attribute
import gaphas.item

class CommentItemPropertyPage(object):
    """
    Property page for Comments
    """
    interface.implements(IPropertyPage)
    component.adapts(items.CommentItem)

    def __init__(self, context):
        self.context = context

    def construct(self):
        page = gtk.VBox()

        label = gtk.Label(_('Comment'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        page.pack_start(label, expand=False)

        buffer = gtk.TextBuffer()
        if self.context.subject.body:
            buffer.set_text(self.context.subject.body)
        text_view = gtk.TextView()
        text_view.set_buffer(buffer)
        text_view.show()
        page.pack_start(text_view)

        buffer.connect('changed', self._on_body_change)
        page.show_all()
        return page

    @transactional
    def _on_body_change(self, buffer):
        self.context.subject.body = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        
component.provideAdapter(CommentItemPropertyPage, name='Properties')


class NamedItemPropertyPage(object):
    """
    An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    interface.implements(IPropertyPage)

    def __init__(self, context):
        self.context = context
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct(self):
        page = gtk.VBox()
        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        subject = self.context.subject
        if not subject:
            return page

        label = gtk.Label(_('Name'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        entry = gtk.Entry()        
        entry.set_text(subject and subject.name or '')
        entry.connect('changed', self._on_name_change)
        hbox.pack_start(entry)
        page.show_all()
        return page

    @transactional
    def _on_name_change(self, entry):
        self.context.subject.name = entry.get_text()
        
component.provideAdapter(NamedItemPropertyPage,
                         adapts=[items.NamedItem], name='Properties')
component.provideAdapter(NamedItemPropertyPage,
                         adapts=[items.NamedLine], name='Properties')


class StereotypePage(object):

    interface.implements(IPropertyPage)

    element_factory = inject('element_factory')

    def __init__(self, context):
        self.context = context
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct(self):
        page = gtk.VBox()
        for i, stereotype in enumerate(self.get_stereotypes()):
            if (i % 3) == 0:
                hbox = gtk.HBox()
                page.pack_start(hbox, expand=False)
            button = gtk.CheckButton()
            button.set_active(stereotype in self.context.subject.appliedStereotype)
            button.connect('toggled', self._on_stereotype_selected, stereotype)
            hbox.pack_start(button, expand=False)
            label = gtk.Label(stereotype.name)
            label.set_justify(gtk.JUSTIFY_LEFT)
            self.size_group.add_widget(label)
            hbox.pack_start(label)
        page.show_all()
        return page

    def get_stereotypes(self):
        stereotype_list = []
        subject = self.context.subject

        # UML specs does not allow to extend stereotypes with stereotypes
        if subject and not isinstance(subject, UML.Stereotype):
            cls = type(subject)

            # find out names of classes, which are superclasses of our subject
            names = set(c.__name__ for c in cls.__mro__ if issubclass(c, UML.Element))

            # find stereotypes that extend out metaclass
            classes = self.element_factory.select(lambda e: e.isKindOf(UML.Class) and e.name in names)

            for class_ in classes:
                for extension in class_.extension:
                    yield extension.ownedEnd.type

    @transactional
    def _on_stereotype_selected(self, button, stereotype):
        subject = self.context.subject
        if button.get_active():
            subject.appliedStereotype = stereotype
        else:
            del subject.appliedStereotype[stereotype]
        
component.provideAdapter(StereotypePage,
                         adapts=[items.ElementItem], name='Stereotypes')
component.provideAdapter(StereotypePage,
                         adapts=[items.LineItem], name='Stereotypes')
    

class ClassPropertyPage(NamedItemPropertyPage):
    """
    Adapter which shows a property page for a class view.
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ClassItem)

    def __init__(self, context):
        super(ClassPropertyPage, self).__init__(context)
        
    def construct(self):
        page = super(ClassPropertyPage, self).construct()

        # Abstract toggle
        hbox = gtk.HBox()
        label = gtk.Label(_("Abstract"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton()
        button.set_active(self.context.subject.isAbstract)
        button.connect('toggled', self._on_abstract_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        hbox.show_all()

        return page

    @transactional
    def _on_abstract_change(self, button):
        self.context.subject.isAbstract = button.get_active()

component.provideAdapter(ClassPropertyPage, name='Properties')


class InterfacePropertyPage(NamedItemPropertyPage):
    """
    Adapter which shows a property page for an interface view.
    """

    interface.implements(IPropertyPage)
    component.adapts(items.InterfaceItem)

    def __init__(self, context):
        super(InterfacePropertyPage, self).__init__(context)
        
    def construct(self):
        page = super(InterfacePropertyPage, self).construct()

        # Fold toggle
        hbox = gtk.HBox()
        label = gtk.Label(_("Fold"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton()
        button.set_active(self.context.folded)
        button.connect('toggled', self._on_fold_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        hbox.show_all()

        return page

    @transactional
    def _on_fold_change(self, button):
        self.context.folded = button.get_active()

component.provideAdapter(InterfacePropertyPage, name='Properties')


class AttributesPage(object):
    """
    An editor for attributes associated with classes and interfaces

    Tagged values are stored in a ListSore: tag, value, taggedValue. taggedValue
    is an UML model element (hidden).
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ClassItem)

    element_factory = inject('element_factory')

    def __init__(self, context):
        super(AttributesPage, self).__init__()
        self.context = context
        
    def construct(self):
        page = gtk.VBox()

        # Show attributes toggle
        hbox = gtk.HBox()
        label = gtk.Label(_("Show attributes"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton()
        button.set_active(self.context.show_attributes)
        button.connect('toggled', self._on_show_attributes_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        # Attributes list store:
        attributes = gtk.ListStore(str, object)
        
        for attribute in self.context.subject.ownedAttribute:
            if not attribute.association:
                attributes.append([attribute.render(), attribute])
        attributes.append(['', None])
        
        self.attributes = attributes
        
        tree_view = gtk.TreeView(attributes)
        tree_view.set_rules_hint(True)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect("edited", self._on_cell_edited, 0)
        tag_column = gtk.TreeViewColumn('Attributes', renderer, text=0)
        tree_view.append_column(tag_column)
        
        page.pack_start(tree_view)
        tree_view.show_all()

        return page
        
    @transactional
    def _on_show_attributes_change(self, button):
        self.context.show_attributes = button.get_active()
        self.context.request_update()
        
    @transactional
    def _on_cell_edited(self, cellrenderertext, path, new_text, col):
        """
        Update the model and UML element based on fresh user input.
        """
        attr = self.attributes[path]

        iter = self.attributes.get_iter(path)

        # Delete attribute if both tag and value are empty
        if not new_text and attr[1]:
            attr[1].unlink()
            self.attributes.remove(iter)
            return

        # Add a new attribute:
        if new_text and not attr[1]:
            a = self.element_factory.create(UML.Property)
            self.context.subject.ownedAttribute = a
            attr[1] = a
            self.attributes.append(['', None])

        # Apply new_text to Attribute
        if attr[1]:
            attr[1].parse(new_text)
            attr[0] = attr[1].render()

component.provideAdapter(AttributesPage, name='Attributes')


class OperationsPage(object):
    """
    An editor for operations associated with classes and interfaces

    Tagged values are stored in a ListSore: tag, value, taggedValue. taggedValue
    is an UML model element (hidden).
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ClassItem)

    element_factory = inject('element_factory')

    def __init__(self, context):
        super(OperationsPage, self).__init__()
        self.context = context
        
    def construct(self):
        page = gtk.VBox()

        # Show operations toggle
        hbox = gtk.HBox()
        label = gtk.Label(_("Show operations"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton()
        button.set_active(self.context.show_operations)
        button.connect('toggled', self._on_show_operations_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        # Operations list store:
        operations = gtk.ListStore(str, object)
        
        for operation in self.context.subject.ownedOperation:
            operations.append([operation.render(), operation])
        operations.append(['', None])
        
        self.operations = operations
        
        tree_view = gtk.TreeView(operations)
        tree_view.set_rules_hint(True)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect("edited", self._on_cell_edited, 0)
        tag_column = gtk.TreeViewColumn('Operation', renderer, text=0)
        tree_view.append_column(tag_column)
        
        page.pack_start(tree_view)
        tree_view.show_all()

        return page
        
    @transactional
    def _on_show_operations_change(self, button):
        self.context.show_operations = button.get_active()
        self.context.request_update()
        
    @transactional
    def _on_cell_edited(self, cellrenderertext, path, new_text, col):
        """
        Update the model and UML element based on fresh user input.
        """
        attr = self.operations[path]

        iter = self.operations.get_iter(path)

        # Delete operation if both tag and value are empty
        if not new_text and attr[1]:
            attr[1].unlink()
            self.operations.remove(iter)
            return

        # Add a new operation:
        if new_text and not attr[1]:
            a = self.element_factory.create(UML.Operation)
            self.context.subject.ownedOperation = a
            attr[1] = a
            self.operations.append(['', None])

        # Apply new_text to Operation
        if attr[1]:
            attr[1].parse(new_text)
            attr[0] = attr[1].render()

component.provideAdapter(OperationsPage, name='Operations')


class TaggedValuePage(object):
    """
    An editor for tagged values associated with elements.

    Tagged values are stored in a ListSore: tag, value, taggedValue. taggedValue
    is an UML model element (hidden).
    """

    interface.implements(IPropertyPage)
    component.adapts(items.NamedItem)

    element_factory = inject('element_factory')
    def __init__(self, context):
        super(TaggedValuePage, self).__init__()
        self.context = context
        
    def construct(self):
        page = gtk.VBox()

        tagged_values = gtk.ListStore(str, str, object)
        
        for tagged_value in self.context.subject.taggedValue:
            tag, value = tagged_value.value.split("=")
            tagged_values.append([tag, value, tagged_value])
        tagged_values.append(['','', None])
        
        self.tagged_values = tagged_values
        
        tree_view = gtk.TreeView(tagged_values)
        tree_view.set_rules_hint(True)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect("edited", self._on_cell_edited, 0)
        tag_column = gtk.TreeViewColumn('Tag', renderer, text=0)
        tree_view.append_column(tag_column)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect("edited", self._on_cell_edited, 1)
        
        value_column = gtk.TreeViewColumn('Value', renderer, text=1)
        tree_view.append_column(value_column)
        
        page.pack_start(tree_view)
        tree_view.show_all()
        return page
        
    @transactional
    def _on_cell_edited(self, cellrenderertext, path, new_text, col):
        """
        Update the model and UML element based on fresh user input.
        """
        tv = self.tagged_values[path]

        tv[col] = new_text

        iter = self.tagged_values.get_iter(path)

        # Delete tagged value if both tag and value are empty
        if not tv[0] and not tv[1] and tv[2]:
            tv[2].unlink()
            self.tagged_values.remove(iter)
        
        # Add a new tagged value:
        elif (tv[0] or tv[1]) and not tv[2]:
            tag = self.element_factory.create(UML.LiteralSpecification)
            tag.value = "%s=%s"%(tv[0], tv[1])
            self.context.subject.taggedValue.append(tag)
            tv[2] = tag
            self.tagged_values.append(['','', None])
        
component.provideAdapter(TaggedValuePage, name='Tagged values')


class DependencyPropertyPage(object):
    """
    An editor for tagged values associated with elements.

    Tagged values are stored in a ListSore: tag, value, taggedValue. taggedValue
    is an UML model element (hidden).
    """

    interface.implements(IPropertyPage)
    component.adapts(items.DependencyItem)

    dependency_types = (
        (_('Dependency'), UML.Dependency),
        (_('Usage'), UML.Usage),
        (_('Realization'), UML.Realization),
        (_('Implementation'), UML.Implementation))

    def __init__(self, context):
        super(DependencyPropertyPage, self).__init__()
        self.context = context
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct(self):
        page = gtk.VBox()

        hbox = gtk.HBox()
        label = gtk.Label(_('Dependency type'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        dependency_type = gtk.ListStore(str)
        
        for t, l in self.dependency_types:
            dependency_type.append([t])
        
        self.dependency_type = dependency_type
        
        combo = gtk.ComboBox(dependency_type)
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)
        combo.connect('changed', self._on_dependency_type_change)
        self.combo = combo

        hbox.pack_start(combo, expand=False)

        page.pack_start(hbox, expand=False)

        hbox = gtk.HBox()

        label = gtk.Label(_('Automatic'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        button = gtk.CheckButton()
        button.set_active(self.context.auto_dependency)
        button.connect('toggled', self._on_auto_dependency_change)
        hbox.pack_start(button)

        page.pack_start(hbox, expand=False)

        page.show_all()

        self.update()

        return page

    def update(self):
        for index, (_, dep_type) in enumerate(self.dependency_types):
            if dep_type is self.context.dependency_type:
                self.combo.set_active(index)
                break

    @transactional
    def _on_dependency_type_change(self, combo):
        self.context.dependency_type = self.dependency_types[combo.get_active()][1]

    @transactional
    def _on_auto_dependency_change(self, button):
        self.context.auto_dependency = button.get_active()


component.provideAdapter(DependencyPropertyPage, name='Properties')


class AssociationPropertyPage(NamedItemPropertyPage):
    """
    """

    interface.implements(IPropertyPage)
    component.adapts(items.AssociationItem)

    def __init__(self, context):
        super(AssociationPropertyPage, self).__init__(context)
        #self.context = context
        #self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct_end(self, title, end):
        hbox = gtk.HBox()
        label = gtk.Label(title)
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        entry = gtk.Entry()        
        entry.set_text(render_attribute(end.subject) or '')
        entry.connect('changed', self._on_end_name_change, end)
        hbox.pack_start(entry)

        combo = gtk.combo_box_new_text()
        for t in ('Unknown navigation', 'Not navigable', 'Navigable'):
            combo.append_text(t)
        
        combo.set_active([None, False, True].index(end.navigability))

        combo.connect('changed', self._on_navigability_change, end)
        hbox.pack_start(combo, expand=False)

        combo = gtk.combo_box_new_text()
        for t in ('No aggregation', 'Shared', 'Composite'):
            combo.append_text(t)
        
        combo.set_active(['none', 'shared', 'composite'].index(end.subject.aggregation))

        combo.connect('changed', self._on_aggregation_change, end)
        hbox.pack_start(combo, expand=False)
        
        return hbox

    def construct(self):
        page = super(AssociationPropertyPage, self).construct()
        
        if not self.context.subject:
            return page

        hbox = gtk.HBox()
        label = gtk.Label(_('Show direction'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        button = gtk.CheckButton()
        button.set_active(self.context.show_direction)
        button.connect('toggled', self._on_show_direction_change)
        hbox.pack_start(button)

        button = gtk.Button(_('Invert direction'))
        button.connect('clicked', self._on_invert_direction_change)
        hbox.pack_start(button)

        page.pack_start(hbox, expand=False)

        hbox = self.construct_end(_('Head'), self.context.head_end)
        page.pack_start(hbox, expand=False)

        hbox = self.construct_end(_('Tail'), self.context.tail_end)
        page.pack_start(hbox, expand=False)

        page.show_all()

        self.update()

        return page

    def update(self):
        pass

    @transactional
    def _on_show_direction_change(self, button):
        self.context.show_direction = button.get_active()

    @transactional
    def _on_invert_direction_change(self, button):
        self.context.invert_direction()

    @transactional
    def _on_end_name_change(self, entry, end):
        end.subject.parse(entry.get_text())

    @transactional
    def _on_navigability_change(self, combo, end):
        end.navigability = (None, False, True)[combo.get_active()]

    @transactional
    def _on_aggregation_change(self, combo, end):
        end.subject.aggregation = ('none', 'shared', 'composite')[combo.get_active()]

component.provideAdapter(AssociationPropertyPage, name='Properties')


class LineStylePage(object):
    """
    Basic line style properties: color, orthogonal, etc.
    """

    interface.implements(IPropertyPage)
    component.adapts(gaphas.item.Line)

    def __init__(self, context):
        super(LineStylePage, self).__init__()
        self.context = context
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct(self):
        page = gtk.VBox()

        hbox = gtk.HBox()
        label = gtk.Label(_('Orthogonal'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        button = gtk.CheckButton()
        button.set_active(self.context.orthogonal)
        button.connect('toggled', self._on_orthogonal_change)
        hbox.pack_start(button)

        page.pack_start(hbox, expand=False)

        hbox = gtk.HBox()
        label = gtk.Label(_('horizontal'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        button = gtk.CheckButton()
        button.set_active(self.context.horizontal)
        button.connect('toggled', self._on_horizontal_change)
        hbox.pack_start(button)

        page.pack_start(hbox, expand=False)

        page.show_all()

        return page

    @transactional
    def _on_orthogonal_change(self, button):
        self.context.orthogonal = button.get_active()

    @transactional
    def _on_horizontal_change(self, button):
        self.context.horizontal = button.get_active()

component.provideAdapter(LineStylePage, name='Style')


class ObjectNodePropertyPage(NamedItemPropertyPage):
    """
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ObjectNodeItem)

    ORDERING_VALUES = ['unordered', 'ordered', 'LIFO', 'FIFO']

    def construct(self):
        page = super(ObjectNodePropertyPage, self).construct()

        subject = self.context.subject
        
        if not subject:
            return page

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        label = gtk.Label(_('Upper Bound'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        entry = gtk.Entry()        
        entry.set_text(subject.upperBound and subject.upperBound.value or '')
        entry.connect('changed', self._on_upper_bound_change)
        hbox.pack_start(entry)

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        label = gtk.Label('Ordering')
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        combo = gtk.combo_box_new_text()
        for v in self.ORDERING_VALUES:
            combo.append_text(v)
        combo.set_active(self.ORDERING_VALUES.index(subject.ordering))
        combo.connect('changed', self._on_ordering_change)
        hbox.pack_start(combo, expand=False)

        button = gtk.CheckButton()
        button.set_active(self.context.show_ordering)
        button.connect('toggled', self._on_ordering_show_change)
        hbox.pack_start(button, expand=False)

        label = gtk.Label('show')
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)

        return page


    def update(self):
        pass

    @transactional
    def _on_upper_bound_change(self, entry):
        value = entry.get_text().strip()
        self.context.set_upper_bound(value)

    @transactional
    def _on_ordering_change(self, combo):
        value = self.ORDERING_VALUES[combo.get_active()]
        self.context.set_ordering(value)

    @transactional
    def _on_ordering_show_change(self, button):
        self.context.show_ordering = button.get_active()
        self.context.set_ordering(self.context.subject.ordering)


component.provideAdapter(ObjectNodePropertyPage, name='Properties')


class JoinNodePropertyPage(NamedItemPropertyPage):
    """
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ForkNodeItem)

    def construct(self):
        page = super(JoinNodePropertyPage, self).construct()

        subject = self.context.subject
        
        if not subject:
            return page

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        label = gtk.Label(_('Join Specification'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        entry = gtk.Entry()        
        entry.set_text(subject.joinSpec and subject.joinSpec.value or '')
        entry.connect('changed', self._on_join_spec_change)
        hbox.pack_start(entry)

        return page

    def update(self):
        pass

    @transactional
    def _on_join_spec_change(self, entry):
        value = entry.get_text().strip()
        self.context.set_join_spec(value)


component.provideAdapter(JoinNodePropertyPage, name='Properties')


class FlowPropertyPage(NamedItemPropertyPage):
    """
    """

    interface.implements(IPropertyPage)
    component.adapts(items.FlowItem)

    def construct(self):
        page = super(FlowPropertyPage, self).construct()

        subject = self.context.subject
        
        if not subject:
            return page

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        label = gtk.Label(_('Guard'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        entry = gtk.Entry()        
        entry.set_text(subject.guard and subject.guard.value or '')
        entry.connect('changed', self._on_guard_change)
        hbox.pack_start(entry)

        return page

    def update(self):
        pass

    @transactional
    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        self.context.set_guard(value)


component.provideAdapter(FlowPropertyPage, name='Properties')


class ComponentPropertyPage(NamedItemPropertyPage):
    interface.implements(IPropertyPage)
    component.adapts(items.ComponentItem)

    def construct(self):
        page = super(ComponentPropertyPage, self).construct()

        subject = self.context.subject
        
        if not subject:
            return page

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        button = gtk.CheckButton()
        button.set_active(subject.isIndirectlyInstantiated)
        button.connect('toggled', self._on_ii_change)
        hbox.pack_start(button, expand=False)

        label = gtk.Label(_('Indirectly Instantiated'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        hbox.pack_start(label, expand=False)

        return page

    def update(self):
        pass

    @transactional
    def _on_ii_change(self, button):
        """
        Called when user clicks "Indirectly Instantiated" check button.
        """
        subject = self.context.subject
        if subject:
            subject.isIndirectlyInstantiated = button.get_active()


component.provideAdapter(ComponentPropertyPage, name='Properties')


# vim:sw=4:et:ai
