from teamrubber.theoracle.infofragment import InfoFragment
import sys

import zLOG
def log_write(message,severity=zLOG.INFO):
    """ Append something to the log """
    zLOG.LOG('Oracle',severity,message)


def safeMethodCall(method,*args,**kwargs):
    """  Safely call a method, wrapping any failures - returns an InfoFragment"""
    result = None
    error = None
    try:
        result = method(*args,**kwargs)
    except Exception, err:
        error = str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1]) 
    return InfoFragment(result,error)
    
def safeAttrGet(object,attr):
    """ Safely get an attribute, wrapping any failures - returns an InfoFragment """
    result = None
    error = None

    #Had to un-generalise this a bit to allow for problems like calling obj.data on an ATFile, especially if the file is big
    #this will go mental and hang the instance.
    
    try:
        #Test if it's a plone object
        result = object[attr]
        if hasattr(result,'portal_type'):
            return InfoFragment("Plone Object: portal_type: %s" % (result.portal_type),error)
    except Exception,err:
        pass
        #error = str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1]) 

    
    try:
        result = getattr(object,attr)
    except Exception,err:
        error = str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1]) 


    truncated = False
    try:
        if len(result) > 1000:
            result = result[:999] 
            truncated = True
    except:
        pass

    
    return InfoFragment(result,error,truncated=truncated)

       
def isFunction(method):
    """ 
        Determine if a method is a callable function.
        Returns True for functions and instancemethods, but false
        for stuff like classes
        
        TODO: Figure out how you're *supposed* to do this, and rewrite.
    """
   
    if '<type' in repr(method.__class__):
        type_name = repr(method.__class__).split("'")[1]
        if type_name in ['function','instancemethod','builtin_function_or_method']:
            return True 
    return False
    

def safe(*args,**kwargs):
    """
        Safely call a method or get an attribute. Results are wrapped
        and returned as an InfoFragment.
        
        Usage: 1. safe(object.method, args, kwargs)
                  Calls object.method(), accepts arguments and named arguments.
                  Example: self.safe(me.getRolesInContext,self.context)
                  
               2. safe(object,'attr')
                  Get attribte 'attr' of object, equivalent to object.attr
    """
    if not isFunction(args[0]):
        return safeAttrGet(*args,**kwargs)
    else:
        return safeMethodCall(*args,**kwargs)
