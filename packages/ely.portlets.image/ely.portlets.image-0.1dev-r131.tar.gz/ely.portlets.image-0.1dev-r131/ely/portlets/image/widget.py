from zope.app.form.browser.widget import DisplayWidget, renderElement
from zope.app.form.browser.textwidgets import FileWidget, escape

from OFS.Image import Image

class ImageWidget(FileWidget):
    """
    The standard FileWidget returns a string instead of an IFile inst,
    which means it will always fail schema validation in formlib.
    """

    def _toFieldValue(self, input):
        value=super(ImageWidget, self)._toFieldValue(input)
        if value:
            value=Image('image','image', value)
        return value

