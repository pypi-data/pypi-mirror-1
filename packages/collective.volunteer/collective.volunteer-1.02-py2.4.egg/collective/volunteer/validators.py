from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implements

class isVolunteerSlotLine:
    __implements__ = IValidator
    
    def __init__(self, name="BaseGalleryTypeValidator", title='', description='', showError=True):
        self.name = name
        self.title = title or name
        self.description = description
        self.showError = showError
        
    def __call__(self, slots, **kwargs):
        for slot in slots:
            split_slots = slot.split('|')
        
            if len(split_slots) == 0:
                return ("You have no provided the correct syntax for a volunteer time.")
        
            if len(split_slots) > 1:
                if len(split_slots[0]) == 0:
                    return ("You must provide a time for every slot.")
            
                if len(split_slots[1]) == 0:
                    return ("You must provide a job description for each volunteer time.")
            
            if len(split_slots) > 2:
            
                if len(split_slots[2]) == 0:
                    return ("If you have a '|' at the end, you must specify a user id for the time.")
            
            if len(split_slots) > 3:
                return ("There is an error with the format you provided.  Seems like you have too many '|'")
            
        return True