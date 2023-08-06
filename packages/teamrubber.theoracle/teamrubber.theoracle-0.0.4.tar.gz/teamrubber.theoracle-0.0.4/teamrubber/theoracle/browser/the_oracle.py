import inspect, sys, pdb

from Products.Five.browser import BrowserView

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import implements, Interface
from zope.component import adapts, queryMultiAdapter, getAdapters
from teamrubber.theoracle.utils import log_write

try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
    pygments_installed = True
except:
    pygments_installed = False
class Oracle(BrowserView):
    """ Oracle """
    
    def __init__(self, context, request):
        self.context=context
        self.request=request
    
    def callMethod(self):
        """ Call specified method """
        if 'method' in self.request.keys():
            try:
                method_name = self.request['method']
                method = getattr(self.context,method_name)
                result = method()
                
                visible_result = "Called: %s\n\nRaw Result: %s\n\nrepr(result): %s\n\nstr(resul): %s\n\n" % (self.request['method'],result,repr(result),str(result))
                return visible_result
            except Exception, err:
                return str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1])
            
        return "No method specified"
    
    def _getSource(self,method,messages=[]):
        """ Actually get the source """
        # TODO: If the attr isn't present, check if it exists in a skin somewhere
        try:
            source = inspect.getsource(method)
        except:
            return None
        style = ""
        processed_source = source
        if pygments_installed:
            style = HtmlFormatter().get_style_defs()
            processed_source = highlight(source, PythonLexer(), HtmlFormatter())
        template = "<html><head><style>%s</style></head><body><pre># Filesystem path: %s</pre><pre>%s</pre></body>" %(style,self._getSourceFilename(method),processed_source)
        return template
    
    def _getSourceFilename(self,method):
        """ Get the filename of the source """
        try:
            filename = inspect.getsourcefile(method)
        except:
            filename = "Unable to get filename"
        return filename
        
    def _import(self,name,fromlist=[]):
        """ Wrapper around import """
        try:
            result = __import__(name,globals(),locals(),fromlist)
        except ImportError:
            result = None
        return result
    
    def getSource(self):
        """ Get source of specified thing """

        if 'object' in self.request.keys():
            object_name = self.request['object']
        else:
            return "No object specified"

        ob_import_explicit = self._import(object_name,object_name.split('.')[-1:])
        ob_import = self._import(object_name)

        ob = ob_import_explicit or ob_import


        if hasattr(self.context,object_name):
            ob = getattr(self.context,object_name)

        source = self._getSource(ob)
        if source:
            return source
        return "Couldn't get the source for that, sorry!" 



    def PDB(self):
        """ Drop to pdb fast """
        if sys.stdout.isatty():
            pdb.set_trace()
    
    def _renderProvider(self,provider):
        try:
            provider.update()
            return provider.render()
        except Exception, err:
            log_write("provider %s failed to render! - %s" % (str(provider),str(err)))
            return None
            
    def getOracleContentProviders(self):
        """ Woo """
        provider = queryMultiAdapter((self.context, self.request,self), IContentProvider, 'latestNews')
        raw_content_providers = getAdapters((self.context, self.request,self), IContentProvider)
        content_providers = {}
        for provider_id,provider_method in raw_content_providers:
            content_providers.update({provider_id:provider_method})
            
        default_providers = [
                            'theoracle.authenticateduserinfo',
                            'theoracle.authenticateduserproperties',
                            'theoracle.contextinfo',
                            'theoracle.contextworkflow',
                            'theoracle.contextATfields',
                            'theoracle.catalogindexes',
                            'theoracle.catalogmetadata',
                            'theoracle.contextattributes',
                            'theoracle.permissions',
                            'theoracle.contextsource',
                            ]

        msg = []

        # Render out the standard providers in order
        for provider_id in default_providers:
            if provider_id in content_providers:
                provider = content_providers[provider_id]
                rendered = self._renderProvider(provider)
                if rendered:
                    msg.append(rendered)


        for provider_id in content_providers:
            if provider_id.startswith('theoracle') and provider_id not in default_providers:
                provider = content_providers[provider_id] 
                rendered = self._renderProvider(provider)
                if rendered:
                    msg.append(rendered)

        return msg

    def getTagline(self):
        """ Sorry, couldn't resist! """
        tls = ['Please keep your arms and legs in at all times',
               'Calming angry bees since 2007',
               'Is never gonna give you up.... Never gonna let you down....',
               'I love egg',
               'If you invite three beekeepers to supper, two of them will be dead by morning. - German beekeeping proverb',
               "I THINK THAT'S TOTALLY OBVIOUS [pushes newbie into water]",
               ]
        
        import random
        return random.choice(tls)