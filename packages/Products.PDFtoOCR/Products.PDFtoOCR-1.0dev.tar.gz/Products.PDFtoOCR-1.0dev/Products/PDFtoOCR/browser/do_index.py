from zope.component import getUtility 

from Products.Five import BrowserView
from Acquisition import aq_inner
from Products.PDFtoOCR.interfaces import IIndex

class DoIndexView(BrowserView):
    """Just some testing / trying out.
    """

    def index(self):
        util = getUtility(IIndex ,'pdf_to_ocr_indexer')
        util.doIndex()
        
    def reindex(self):
        util = getUtility(IIndex ,'pdf_to_ocr_indexer')
        util.doReindex()
        
    def reinit(self):
        util = getUtility(IIndex ,'pdf_to_ocr_indexer')
        util.reinit()
        return 'Queue is reset!'

    def getUIDInfo(self, uid):
        context = aq_inner(self.context)
        results = context.uid_catalog(UID=uid)
        doc = dict()
        if results:
            item = results[0]
            doc['Title'] = item.Title
            doc['Description'] = item.Description()
            doc['id'] = item.id
            doc['url'] = item.getURL()
        return doc 


    def queueStatus(self):
        util = getUtility(IIndex ,'pdf_to_ocr_indexer')
        files = util._fileList
        return  [self.getUIDInfo(f) for f in files]

    def historyStatus(self):
        util = getUtility(IIndex ,'pdf_to_ocr_indexer')
        files = util._history
        return  [self.getUIDInfo(f) for f in files]




