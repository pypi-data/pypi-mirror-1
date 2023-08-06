class InfoFragment:
    """ A value for returning to the page template """
    has_error = False
    truncated = False
    value = ''
    error_message = ''
    
    def getClass(self):
        if self.has_error:
            return 'error'
        elif self.truncated:
            return 'truncated'
        return ''
    
    def __init__(self,value,error_message=None,truncated=False):
        """ Constructor - takes an value to display and optionally an error message """
        self.value = value
        self.truncated = truncated
        if error_message!=None:
            self.error_message = error_message
            self.has_error = True

                
    def __call__(self):
        """ Return something sensible """
        if self.has_error:
            return self.error_message
        return self.value