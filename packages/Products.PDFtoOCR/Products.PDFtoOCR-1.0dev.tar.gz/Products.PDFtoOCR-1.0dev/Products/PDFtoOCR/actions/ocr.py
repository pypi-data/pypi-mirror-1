from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from zope.component import adapts, getUtility
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface, implements
from zope.formlib import form
from zope import schema

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 
from plone.app.vocabularies.groups import GroupsSource
from plone.app.vocabularies.users import UsersSource
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode

from Products.PDFtoOCR.interfaces import IIndex

class IOCRAction(Interface):
    """Definition of the configuration available for the OCR action
    """

class OCRAction(SimpleItem):
    """
    The implementation of the action defined before
    """
    implements(IOCRAction, IRuleElementData)

    element = 'plone.actions.PDFtoOCR'

    @property
    def summary(self):
        return _(u"DO OCR STUFF")

    

class OCRActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IOCRAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        context = aq_inner(self.context)

        obj = self.event.object

        contentType = obj.getContentType()

        util = getUtility(IIndex, 'pdf_to_ocr_indexer')
        util.addFile(obj.UID())
        
        return True


class OCRAddForm(AddForm):
    """
    An add form for the OCR action
    """
    form_fields = form.FormFields(IOCRAction)
    label = _(u"Add OCR Action for indexing PDF documents")
    description = _(u"Index PDF documents using OCR. Used for document where pdf2text doesn't work. Don't forget to setup cron4plone")
    form_name = _(u"Add PDF2OCR action")

    def create(self, data):
        a = OCRAction()
        form.applyChanges(a, self.form_fields, data)
        return a



class OCREditForm(EditForm):
    """
    An edit form for the OCR action
    """
    form_fields = form.FormFields(IOCRAction)
    label = _(u"Add OCR Action for indexing PDF documents")
    description = _(u"Index PDF documents using OCR. Used for document where pdf2text doesn't work. Don't forget to setup cron4plone")
    form_name = _(u"Add PDF2OCR action")



