# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: widgets.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
"""
Clases de widgets especiales

@author: Juan Pablo Gimenez
@contact: jpg@rcom.com.ar
"""
__author__ = """Juan Pablo Gimenez <jpg@rcom.com.ar>"""
__docformat__ = 'plaintext'

from zope.app.form.browser.itemswidgets import OrderedMultiSelectWidget as BaseOrderedMultiSelectWidget, \
                                        MultiSelectWidget as BaseMultiSelectWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

def OrderedMultiSelectionWidgetFactory( field, request ):
    """ Factory para construir OrderedMultiSelectionWidgets
    """
    vocabulary = field.value_type.vocabulary
    if not request.debug:
        widget = OrderedMultiSelectionWidget( field, vocabulary, request )
    else:
        widget = BaseMultiSelectWidget( field, vocabulary, request)

    return widget

def MultiSelectionWidgetFactory( field, request ):
    """ Factory para construir MultiSelectionWidgets
    """
    vocabulary = field.value_type.vocabulary
    if not request.debug:
        widget = MultiSelectionWidget( field, vocabulary, request)
    else:
        widget = BaseMultiSelectWidget( field, vocabulary, request)

    return widget

class OrderedMultiSelectionWidget(BaseOrderedMultiSelectWidget):
    """ Widget para listas de seleccion ordenadas
    """
    template = ViewPageTemplateFile('templates/ordered-selection.pt')

    def selected(self):
        """Return a list of tuples (text, value) that are selected."""
        # Get form values
        values = self._getFormValue()
        # Not all content objects must necessarily support the attributes
        if hasattr(self.context.context, self.context.__name__):
            # merge in values from content
            for value in self.context.get(self.context.context):
                if value not in values:
                    values.append(value)
        terms = [self.vocabulary.getTerm(value)
                 for value in values if value in self.vocabulary ]
        return [{'text': self.textForValue(term), 'value': term.token}
                for term in terms]

class MultiSelectionWidget(OrderedMultiSelectionWidget):
    """ Widget para listas de seleccion no ordenadas
    """
    template = ViewPageTemplateFile('templates/unordered-selection.pt')
