# vim:sw=4:et
"""
Feature diagram item. Feature is a super class of both Attribute, Operations and
Methods.
"""

from gaphor import UML
from gaphas.item import Item
from gaphor.diagram import DiagramItemMeta
from gaphor.diagram.diagramitem import DiagramItem
from gaphas.util import text_extents, text_set_font, text_align, text_underline
from gaphor.diagram import font

class FeatureItem(DiagramItem):
    """
    FeatureItems are model elements who recide inside a ClassifierItem, such
    as methods and attributes. Those items can have comments attached, but only
    on the left and right side.
    Note that features can also be used inside objects.
    """

    def __init__(self, id=None):
        DiagramItem.__init__(self, id)
        self.width = 0
        self.height = 0
        self.text = ''
        self.font = font.FONT
        # Fool unlink code (attribute is not a gaphas.Item):
        self.canvas = None
        self.watch('subject.isStatic', self.on_feature_is_static)


    def save(self, save_func):
        DiagramItem.save(self, save_func)
        

    def postload(self):
        if self.subject:
            self.text = self.subject.render()
        self.on_feature_is_static(None)


    def on_feature_is_static(self, event):
        ##
        ## TODO: How do I underline text??
        ##
        self.font = (self.subject and self.subject.isStatic) \
                and font.FONT_ABSTRACT_NAME or font.FONT_NAME
        self.request_update()


    def get_size(self, update=False):
        """
        Return the size of the feature. If update == True the item is
        directly updated.
        """
        return self.width, self.height


    def get_text(self):
        return ''


    def update_size(self, text, context):
        if text:
            cr = context.cairo
            self.width, self.height = text_extents(cr, text)
        else:
            self.width, self.height = 0, 0


    def pre_update(self, context):
        self.update_size(self.subject.render(), context)


    def point(self, pos):
        """
        """
        return distance_rectangle_point((0, 0, self.width, self.height), pos)


    def draw(self, context):
        cr = context.cairo
        text_set_font(cr, self.font)
        text_align(cr, 0, 0, self.subject.render() or '', align_x=1, align_y=1)


class AttributeItem(FeatureItem):

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)

        self.watch('subject<NamedItem>.name') \
            .watch('subject<Property>.isDerived') \
            .watch('subject<Property>.visibility') \
            .watch('subject<Property>.isStatic') \
            .watch('subject<Property>.lowerValue<LiteralSpecification>.value') \
            .watch('subject<Property>.upperValue<LiteralSpecification>.value') \
            .watch('subject<Property>.defaultValue<LiteralSpecification>.value') \
            .watch('subject<Property>.typeValue<LiteralSpecification>.value') \
            .watch('subject<Property>.taggedValue<LiteralSpecification>.value')


    def postload(self):
        if self.subject:
            self.text = self.subject.render()

    def draw(self, context):
        if self.subject.isStatic:
            cr = context.cairo
            text_set_font(cr, self.font)
            text_underline(cr, 0, 0, self.subject.render() or '')
        else:
            super(AttributeItem, self).draw(context)


class OperationItem(FeatureItem):

    def __init__(self, id=None):
        FeatureItem.__init__(self, id)
        
        self.watch('subject.name') \
            .watch('subject.isAbstract', self.on_operation_is_abstract) \
            .watch('subject.visibility') \
            .watch('subject.taggedValue<LiteralSpecification>.value') \
            .watch('subject.returnResult.lowerValue<LiteralSpecification>.value') \
            .watch('subject.returnResult.upperValue<LiteralSpecification>.value') \
            .watch('subject.returnResult.typeValue<LiteralSpecification>.value') \
            .watch('subject.returnResult.taggedValue<LiteralSpecification>.value') \
            .watch('subject.formalParameter.lowerValue<LiteralSpecification>.value') \
            .watch('subject.formalParameter.upperValue<LiteralSpecification>.value') \
            .watch('subject.formalParameter.typeValue<LiteralSpecification>.value') \
            .watch('subject.formalParameter.defaultValue<LiteralSpecification>.value') \
            .watch('subject.formalParameter.taggedValue<LiteralSpecification>.value')


    def postload(self):
        if self.subject:
            self.text = self.subject.render()
        self.on_operation_is_abstract(None)

    def on_operation_is_abstract(self, event):
        self.font = (self.subject and self.subject.isAbstract) \
                and font.FONT_ABSTRACT_NAME or font.FONT_NAME
        self.request_update()



class SlotItem(FeatureItem):
    def __init__(self, id=None):
        FeatureItem.__init__(self, id)

#    def on_feature_value(self, event):
#        element = event.element
#        subject = self.subject
#        if subject and element in (subject.lowerValue, subject.upperValue, subject.defaultValue, subject.typeValue, subject.taggedValue):
#            self.request_update()


    def _render_slot(self):
        slot = self.subject
        return '%s = "%s"' % (slot.definingFeature.name, slot.value[0].value)

    def pre_update(self, context):
        self.update_size(self._render_slot(), context)
        #super(AttributeItem, self).pre_update(context)

    def draw(self, context):
        cr = context.cairo
        text_set_font(cr, font.FONT)
        text_align(cr, 0, 0, self._render_slot(), align_x=1, align_y=1)


class StereotypeNameItem(FeatureItem):
    def __init__(self, id=None):
        FeatureItem.__init__(self, id)

#    def on_feature_value(self, event):
#        element = event.element
#        subject = self.subject
#        if subject and element in (subject.lowerValue, subject.upperValue, subject.defaultValue, subject.typeValue, subject.taggedValue):
#            self.request_update()


    def _render_name(self):
        return UML.model.STEREOTYPE_FMT % self.subject.name


    def pre_update(self, context):
        self.update_size(self._render_name(), context)
        #super(AttributeItem, self).pre_update(context)

    def draw(self, context):
        cr = context.cairo
        text_set_font(cr, font.FONT)
        text_align(cr, 0, 0, self._render_name(), align_x=0.5, align_y=0.5)


# vim:sw=4:et:ai
