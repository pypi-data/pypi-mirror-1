import inspect
from Products.Five.browser import BrowserView

try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
    pygments_installed = True
except:
    pygments_installed = False
    
class Oracode(BrowserView):
    """ Oracode """
    
    def __init__(self, context, request):
        self.context=context
        self.request=request
    
    def _formatSource(self,source):
        """ Pretty up some source code """
        processed_source = source
        style=""
        if pygments_installed:
            style = HtmlFormatter().get_style_defs()
            processed_source = highlight(source, PythonLexer(), HtmlFormatter())
        return style,processed_source
    
    def _getSource(self,method):
        """ Actually get the source """
        source = None
        
        # Try and get source for FS code objects
        try:
            source = inspect.getsource(method)
            code_type = 'Filesystem Code'
        except TypeError:
            pass
        
        # Try and get ZMI objects
        if hasattr(method,'meta_type'):
            if method.meta_type in ['Filesystem Script (Python)', 
                                    'Filesystemtem Controller Validator',
                                    'Filesystem Controller Python Script',
                                    'Script (Python)',
                                    'Controller Python Script',
                                    'Controller Validator']:
                source = "%s" % (method.read())
                code_type = method.meta_type
        
        
        #from zope.publisher.interfaces import IRequest
        #from zope.component import adapts, queryMultiAdapter, getAdapters        
        #a = getAdapters((self.context, self.request, self), IRequest)
        #import pdb
        #pdb.set_trace()
        
        if source:
            result = {'filename':self._getSourceFilename(method),'source':source,'len':self._getSourceLength(source),'type':code_type}
            return result
        return {'error':"Couldn't get the source for that, sorry!"}

    def _getSourceLength(self,source):
        """ Get the length of some source """
        split_source = source.split('\n')
        return len(split_source)
            
    def _getSourceFilename(self,method):
        """ Get the filename of the source """
        try:
            filename = inspect.getsourcefile(method)
        except:
            filename = None
        return filename
        
    def _import(self,name,fromlist=[]):
        """ Wrapper around import """
        try:
            result = __import__(name,globals(),locals(),fromlist)
        except ImportError:
            result = None
        return result
    
    def getSubstringLineNumber(self,full_source,method_source):
        """ Get the line number of a method given the full source """
        if method_source not in full_source:
            return -1

        f_lines = full_source.split('\n')
        m_lines = method_source.split('\n')
        
        # This is ridiculously clunky.
        m_pos = 0
        f_pos = 0
        result = -1
        for line in f_lines:
            if line == m_lines[m_pos]:
                m_pos += 1
                if result == -1: 
                    result = f_pos
            else:
                m_pos = 0
                result = -1
            if m_pos == len(m_lines)-1:
                return result
            f_pos += 1
        return -2
            
    
    def getSource(self):
        """ Get source of specified thing """
        result = {'error':None,'parent':None,'css':'','source':'','type':None}

        if 'object' in self.request.keys():
            object_name = self.request['object']
        else:
            result['error'] = "No object specified"
            return result
            
        # These cover dotted names, kinda rough really.
        ob_import_explicit = self._import(object_name,object_name.split('.')[-1:])
        ob_import = self._import(object_name)
        ob = ob_import_explicit or ob_import

        # This is as an attribute
        if hasattr(self.context,object_name):
            ob = getattr(self.context,object_name)
            #ob_parent = ob.im_class

        result.update(self._getSource(ob))
        if hasattr(ob,'__module__'):
            result['parent'] = ob.__module__

        result['css'],result['source'] = self._formatSource(result['source'])
        return result
