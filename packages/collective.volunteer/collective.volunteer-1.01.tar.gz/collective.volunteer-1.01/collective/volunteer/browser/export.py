from Products.Five import BrowserView
import csv, time
from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName
class CSV(BrowserView):
    
    def __call__(self):
        pm = getToolByName(self.context, 'portal_membership')
        utils = getToolByName(self.context, 'plone_utils')
        
        buffer = StringIO()
        writer = csv.writer(buffer, quoting = csv.QUOTE_ALL)
        
        writer.writerow(('Time', 'Job', 'Assignment'))
        for slot in self.context.getTimesAvailable():
            slot = slot.split('|')
            if len(slot) == 3:
                slot[2] = pm.getMemberById(slot[2]).getProperty('fullname')
                
            writer.writerow(slot)
            
        value = buffer.getvalue()
        value = unicode(value, 'utf-8').encode('iso-8859-1', 'replace')
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader('Content-Disposition', 'attachment;filename=%s-%s.csv' % (
            utils.normalizeString(self.context.Title()), 
            time.strftime("%Y%m%d-%H%M")
        ))
        
        return value