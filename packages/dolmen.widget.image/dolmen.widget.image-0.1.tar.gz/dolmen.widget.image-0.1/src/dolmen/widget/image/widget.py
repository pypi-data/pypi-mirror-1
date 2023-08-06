# -*- coding: utf-8 -*-

import grokcore.view as grok
import megrok.z3cform.base as z3cform

from zope.interface import Interface
from dolmen.file import IImageField
from dolmen.widget.file import FileWidget

 
class ImageWidget(FileWidget):
    """A widget for a named file object. It handles specificly an
    image, displaying a thumbnail on both the edit and display form.
    """
    klass = u'image-widget'
    value = None

    @property
    def preview_url(self):
        if self.field is None or self.ignoreContext or not self.url:
            return None
        return '%s/++thumbnail++%s.preview' % (self.url, self.field.__name__)


class ImageWidgetInput(z3cform.WidgetTemplate):
    grok.context(Interface)
    grok.layer(z3cform.IFormLayer)
    grok.template('templates/input.pt')
    z3cform.directives.field(IImageField)
    z3cform.directives.widget(ImageWidget)
    z3cform.directives.mode(z3cform.INPUT_MODE)


class ImageWidgetDisplay(z3cform.WidgetTemplate):
    grok.context(Interface)
    grok.layer(z3cform.IFormLayer)
    grok.template('templates/display.pt')
    z3cform.directives.field(IImageField)
    z3cform.directives.widget(ImageWidget)
    z3cform.directives.mode(z3cform.DISPLAY_MODE)


@grok.implementer(z3cform.IFieldWidget)
@grok.adapter(IImageField, z3cform.IFormLayer)
def ImageFieldWidget(field, request):
    """IFieldWidget factory for ImageWidget."""
    return z3cform.widget.FieldWidget(field, ImageWidget(request))
