import inspect, sys, pdb

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import implements, Interface
from zope.component import adapts, queryMultiAdapter, getAdapters

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
        
    def getSource(self):
        """ Get source of specified method """
        try:
            from pygments import highlight
            from pygments.lexers import PythonLexer
            from pygments.formatters import HtmlFormatter
            formatted = True
        except:
            formatted = False

        if 'method' in self.request.keys():
            try:
                actual_attr = getattr(self.context,self.request['method'])
                source = inspect.getsource(actual_attr)
                style = ""
                processed_source = source
                if formatted:
                    style = HtmlFormatter().get_style_defs()
                    processed_source = highlight(source, PythonLexer(), HtmlFormatter())
                template = "<html><head><style>%s</style></head><body><pre>%s</pre></body>" %(style,processed_source)
                return template
            except:
                return "Couldn't get source, sorry!"
                
            # TODO: If the attr isn't present, check if it exists in a skin somewhere


                
        return "No method specified"

    def PDB(self):
        """ Drop to pdb fast """
        if sys.stdout.isatty():
            pdb.set_trace()
    
    def _renderProvider(self,provider):
        try:
            provider.update()
            return provider.render()
        except Exception, err:
            print "Oracle provider %s failed to render! - %s" % (str(provider),str(err))
            
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
                            ]

        msg = []

        # Render out the standard providers in order
        for provider_id in default_providers:
            if provider_id in content_providers:
                provider = content_providers[provider_id]
                msg.append(self._renderProvider(provider))


        for provider_id in content_providers:
            if provider_id.startswith('theoracle') and provider_id not in default_providers:
                provider = content_providers[provider_id] 
                msg.append(self._renderProvider(provider))

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