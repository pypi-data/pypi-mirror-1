from zope.component import getMultiAdapter, getUtility
from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from Products.DigestoContentTypes.utilities.interfaces import INormativaTypes

class DynamicSequenceWidget(SimpleInputWidget):

    __call__ = ViewPageTemplateFile('templates/widget.pt')
    
    def _getFormInput(self):
        value = super(DynamicSequenceWidget, self)._getFormInput()
        # Make sure that we always retrieve a list object from the
        # request, even if only a single item or nothing has been
        # entered
        if value is None:
            value = []
        if not isinstance(value, list):
            value = [value]
        return value

    def hasInput(self):
        return (self.name + '.marker') in self.request.form

    def hidden(self):
        s = ''
        for value in self._getFormValue():
            widget = getMultiAdapter(
                (self.context.value_type, self.request), IInputWidget)
            widget.name = self.name
            widget.setRenderedValue(value)
            s += widget.hidden()
        return s

class NormativaDynamicSequenceWidget(DynamicSequenceWidget):
    def _getFormValue(self):
        cu = getUtility(INormativaTypes)
        return cu.types

