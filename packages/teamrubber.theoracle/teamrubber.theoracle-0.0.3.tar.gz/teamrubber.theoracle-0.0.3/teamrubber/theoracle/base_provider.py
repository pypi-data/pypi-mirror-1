from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import implements, Interface
from zope.component import adapts
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class BaseProvider(object):
	implements(IContentProvider)
	adapts(Interface, IDefaultBrowserLayer, Interface)

	template = None
	
	def __init__(self, context, request, view):
		self.context = context
		self.request = request
		self.__parent__ = view
		template_root = 'providers/templates/'
		if self.template:
			self.template_object = ViewPageTemplateFile(template_root + self.template)
		else:
			self.template_object = None
		
		
	def update(self):
		pass

	def render(self):
		if self.template_object:
			return self.template_object(self,view=self)
		else:
			return self.__call__()
