from Acquisition import aq_inner
from Products.Five import BrowserView
from collective.contentleadimage.interfaces import ILeadImageable

class isObjectLeadImageable(BrowserView):
    def query(self):
        return ILeadImageable.providedBy(aq_inner(self.context))
    