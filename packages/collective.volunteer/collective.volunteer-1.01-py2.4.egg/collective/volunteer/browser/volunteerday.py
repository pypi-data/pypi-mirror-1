from plone.memoize.instance import memoize
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class View(BrowserView):
    
    template = ViewPageTemplateFile('volunteerday_view.pt')
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.portal_membership = getToolByName(self.context, 'portal_membership')
    
    def __call__(self):
        return self.template()
    
    @memoize
    def times(self):
        return [time.split("|") for time in self.context.getTimesAvailable()]
    
    def getMemberName(self, id):
        member = self.portal_membership.getMemberById(id)
        return member.getProperty('fullname')
    
class Ajax(BrowserView):
    
    def __call__(self):
        method = getattr(self, self.request.get("method"))
        return method()
        
    def remove_volunteer(self):
        pm = getToolByName(self.context, 'portal_membership')
        
        member = pm.getAuthenticatedMember()
        
        index = int(self.request.get('id').split("-")[1])
        slots = list(self.context.getTimesAvailable())
        slot = slots[index]
        
        time, desc, user_id = slot.split("|")        
        
        if member and member.getProperty('id') == user_id:

            slots[index] = time + "|" + desc
            self.context.setTimesAvailable(slots)
            
            return "[{ele_id: '%s'}]" % self.request.get('id').strip()
        else:
            return False
        
    def volunteer(self):
        pm = getToolByName(self.context, 'portal_membership')
        
        member = pm.getAuthenticatedMember()
        
        if member:
            index = int(self.request.get('id').split('-')[1])
            slots = list(self.context.getTimesAvailable())
            slot = slots[index]
            
            time, desc = slot.split("|")
            slots[index] = time + "|" + desc + "|" + member.getProperty('id')
            self.context.setTimesAvailable(tuple(slots))
            
            return "[{user_id: '%s', ele_id: '%s'}]" % (member.getProperty('fullname'), self.request.get('id').strip())
        else:
            return False
        
        