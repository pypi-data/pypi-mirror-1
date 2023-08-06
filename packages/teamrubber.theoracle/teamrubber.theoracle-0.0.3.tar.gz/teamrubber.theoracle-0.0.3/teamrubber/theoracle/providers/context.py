from teamrubber.theoracle.base_provider import BaseProvider
from teamrubber.theoracle.infofragment import InfoFragment
from teamrubber.theoracle.utils import safe

from Products.CMFCore.utils import getToolByName
import inspect,sys

class ContextBase(object):
    pass


class ContextSource(BaseProvider):
    template = "ContextSource.pt"
    
    def getSource(self):
        try:
            return InfoFragment(inspect.getsource(self.context.__class__))
        except Exception,err:
            return InfoFragment('',error_message=str(err))                
    
    def getFormattedSource(self):
        source = inspect.getsource(self.context.__class__)
        try:
            from pygments import highlight
            from pygments.lexers import PythonLexer
            from pygments.formatters import HtmlFormatter

            return InfoFragment(highlight(source, PythonLexer(), HtmlFormatter()))
        except:
            return self.getSource()

    def getCSS(self):
        from pygments.formatters import HtmlFormatter
        return HtmlFormatter().get_style_defs()

class ContextAttributes(ContextBase,BaseProvider):
    template = "ContextAttributes.pt"
    
    methods = []
    attributes = []
    unknowns = []
    
    def getFunctionArgs(self,method):
        """ Get the arguments for a method source """
        source = inspect.getsource(method)
        result = source
        def_start = source.index('def ')
        result = result[def_start+4:].strip()
        open = 0
        close = 0
        for i in range(0,len(result)):
            next_char = result[i]
            if next_char == '(':
                if open==0:
                    start_point = i+1
                open = open +1
            if next_char == ')':
                open = open - 1
                if open==0:
                    end_point = i
                    break
                    
        result = result[start_point:end_point]
        return result
    
    def isFunction(self,method):
        if '<type' in repr(method.__class__):
            type_name = repr(method.__class__).split("'")[1]
            if type_name in ['function','instancemethod','builtin_function_or_method']:
                return True 
        return False
    
    def getDocString(self,actual_attr):
        """ Get docstring """
        return str(actual_attr.__doc__)

    def getModule(self,actual_attr):
        """ Get module name """
        return str(actual_attr.__module__)
    

    
    def update(self):
        """ Dir context, splits the result into methods, attributes and unknowns.  Tries to remove content items from the attributes list. """
        self.methods = []
        self.attributes = []
        self.unknowns = []
        everything = dir(self.context)
        try:
            contents = self.context.getObjectIds()
        except:
            contents = []
        
        for attr_name in everything:
            attr = getattr(self.context,attr_name,None)
            try:
                if self.isFunction(attr):
                    self.methods.append({
                                        'id': attr_name,
                                        'doc': safe(self.getDocString,attr),
                                        'module': safe(self.getModule,attr),
                                        'src':safe(inspect.getsource,attr),
                                        'args':safe(self.getFunctionArgs,attr),
                                    })
                else:
                    if str(attr_name) not in contents:
                        self.attributes.append({'id':attr_name,'value':safe(self.context,attr_name)})
            except:
                self.unknowns.append({'id':attr_name,'error':InfoFragment('',error_message=str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1]) )})

    def getMethods(self):
        return self.methods
    
    def getAttributes(self):
        return self.attributes
    
    def getUnknowns(self):
        return self.unknowns

class ContextPermissions(ContextBase,BaseProvider):
    template = "ContextPermissions.pt"
    
    valid_permissions = []
    invalid_permissions = []
    
    def getValidPermissions(self):
        return self.valid_permissions
    
    def getInvalidPermissions(self):
        return self.invalid_permissions
        
    def update(self):
        """ Get permissions and test whether they are valid for authenticatedmember in context """
        try:
            self.valid_permissions = []
            self.invalid_permissions = []
            
            if hasattr(self.context,'possible_permissions'):
                permissions = self.context.possible_permissions()
            else:
                permissions = []
            
            checkPermission = getToolByName(self.context,'portal_membership').checkPermission
        
            for permission in permissions:
                if checkPermission(permission,self.context):
                    self.valid_permissions.append(permission)
                else:
                    self.invalid_permissions.append(permission)
        except Exception,err:
            print err
            
        

class ContextInfo(ContextBase,BaseProvider):
    template = 'ContextInfo.pt'

    def getTemporary(self,obj):
        """ Is an object temporary, ie part of portal_factory """
        factory_tool = getToolByName(self.context,'portal_factory')
        return factory_tool.isTemporary(obj)

    def getPath(self,obj):
        """ Get physical path """
        physicalpath = obj.getPhysicalPath()
        return "%s" % ("/".join(physicalpath))

    def getContextInfo(self):
        """ Return important info about context """
        context = self.context
        result = {
                      'id':                safe(context,'id'),
                      'portal_type':       safe(context,'portal_type'),                  
                      'url':               safe(context.absolute_url),
                      'path':              safe(self.getPath,context),
                      'temporary':         safe(self.getTemporary,context)
                  }
        return result


class ContextWorkflow(ContextBase,BaseProvider):
    template='ContextWorkflow.pt'
    
    workflow_tool = None

    def update(self):
        self.workflow_tool = getToolByName(self.context,'portal_workflow')
    
    def getReviewState(self):
        """ Get workflow state """
        return safe(self.workflow_tool.getInfoFor,self.context,'review_state')

    def getWorkflow(self):
        """ Get Workflow For Object """
        try:
            return InfoFragment(self.workflow_tool.getWorkflowsFor(self.context))
        except Exception, err:
            return InfoFragment('',error_message=str(err))
            
    def getWorkflowHistory(self):
        """ Get workflow history for object """
        try:
            workflow_history = self.context.workflow_history
            if len(workflow_history) > 0:
                return InfoFragment(workflow_history[workflow_history.keys()[0]])
        except Exception, err:
            return InfoFragment('',error_message="No workflow defined for this object")


class ContextATFields(BaseProvider):
    template='ContextATFields.pt'
    
    def getFieldMethods(self,field):
        method_names = ['getEditAccessor','getIndexAccessor','getAccessor','getMutator']
        
        result = {}
        for method_name in method_names:
            try:
                method = getattr(field,method_name)
                field_text = method(self.context).__name__
                result[method_name] = InfoFragment(field_text)
            except Exception, err:
                result[method_name] = InfoFragment('',error_message="Failed: " + str(err))
        return result
            
    def getATFields(self):
        """ Get schema fields for AT content. """
        try:    
            fields = self.context.Schema().fields()
            result = []
            for field in fields:
                if field is not None:
                    field_methods = self.getFieldMethods(field)
                    new_field = {
                                'id': safe(field.getName),
                                'type':safe(field.getType),
                                'mode':safe(field,'mode'),
                                'accessor': field_methods['getAccessor'],
                                'edit_accessor': field_methods['getEditAccessor'],
                                'index_accessor': field_methods['getIndexAccessor'],                                                                
                                'mutator': field_methods['getMutator'],
                                'vocabulary': safe(field,'vocabulary'),
                                'ismetadata': safe(field,'ismetadata'),
                                'required': safe(field,'required'),
                                'searchable': safe(field,'searchable'),
                                'regfield': safe(field,'regfield'),
                            }
                            
                    result.append(new_field)

            return InfoFragment(result)
        except Exception, err:
            return InfoFragment([],error_message="Couldn't get Schema, this is either because this object doesn't have one, or something went wrong.")