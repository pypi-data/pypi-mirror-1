import logging

from zope.app import zapi
from zope.component import getUtility 
from zope.interface import implements
from persistent import Persistent
from persistent.list import PersistentList

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from OFS.SimpleItem import SimpleItem

from Products.PDFtoOCR.interfaces import IIndex

logger = logging.getLogger('Products.PDFtoOCR')


class Index(Persistent, SimpleItem):
    """
    """ 

    def __init__(self):
        self._fileList = set()
        self._history = PersistentList()

    def reinit(self):
        self.__init__()

    def _changes(self):
        self._p_changed = 1 # for persistence..    
 
    def addFile(self, uid):
        self._fileList.add(uid)
        self._changes()

    def updateHistory(self, uid):
        self._history.append(uid)
        if len(self._history) > 10:
            self._history = self._history[:10]

    def doIndex(self):
        """ Index the PDF documents in the filelist queue
        """
        documents = []
        filesDone = set()
        fileList = self._fileList
        portal = getUtility(ISiteRoot)
        catalog = getToolByName(portal, 'portal_catalog')

        logger.info('Start OCR indexing of pdf documents')
        logger.info('Got %s docs in file list' % len(fileList))

        # Proces pdf files for indexing
        # remove all other files
        for uid in fileList: 
            results = portal.uid_catalog(UID=uid)

            if results:
                file = results[0].getObject()
                if file.getContentType() == 'application/pdf':
                   self.ocrIndexPDF(file)
            filesDone.add(uid)

        # Remove all non-pdf documents
        self._fileList = self._fileList - filesDone
        self._changes() 
        logger.info('OCR indexing of pdf documents done')


    def doReindex(self):
        """ Indexes all pdf files
        Warning: this can take a while when you have many pdf docs
        """
        logger.info('Start OCR reindexing of pdf documents')
        portal = getUtility(ISiteRoot)
        catalog = getToolByName(portal, 'portal_catalog')
        results = catalog(Type='File')
        logger.info('Got %s docs in file list' % len(results))

        for brain in results:
            document = brain.getObject()
            if document.getContentType() == 'application/pdf':
                self.ocrIndexPDF(document)
        
        logger.info('OCR reindexing of pdf documents done')

    def ocrIndexPDF(self, document):
        """ Does OCR indexing on pdf documents
        """
        logger.info('OCR processing %s' % document.getId())
    
        language = document.getDocLanguage()
        if language == 'default':
            portal = getUtility(ISiteRoot)
            properties = getToolByName(portal, 'portal_properties')
            language = properties.site_properties.default_language

        output = str(document.getFile().data)
        text = self.pdf_to_ocr(output, language)
        # Do we need this?
        #words = self._process_words(text, language)

        if text:
            document.setTextFromOcr(text)
            document.reindexObject() 
            self.updateHistory(document.UID())

