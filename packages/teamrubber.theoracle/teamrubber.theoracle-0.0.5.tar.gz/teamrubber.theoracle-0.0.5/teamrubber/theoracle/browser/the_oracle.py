import sys, pdb

from Products.Five.browser import BrowserView

from zope.contentprovider.interfaces import IContentProvider
from zope.component import getAdapters
from teamrubber.theoracle.utils import log_write

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
    
    def PDB(self):
        """ Drop to pdb fast """
        try:
            # Get some nice stuff imported.
            from Products.CMFCore.utils import getToolByName
            import inspect
        except:
            pass
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