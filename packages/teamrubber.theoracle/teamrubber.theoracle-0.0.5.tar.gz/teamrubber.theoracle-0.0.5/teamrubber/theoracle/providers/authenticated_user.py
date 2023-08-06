from teamrubber.theoracle.base_provider import BaseProvider
from teamrubber.theoracle.infofragment import InfoFragment
from teamrubber.theoracle.utils import safe

from Products.CMFCore.utils import getToolByName



class AuthenticatedUserInfo(BaseProvider):
    template = 'AuthenticatedUserInfo.pt'

    def getAuthMemberInfo(self):
        """ Return basic info about a member """
        me = self.getAuthenticatedMember()
        result = {
                  'id':                     safe(self.getMemberId,me),
                  'portal_type':            safe(me,'portal_type'),
                  'roles':                  safe(me.getRoles),
                  'contextroles':           safe(me.getRolesInContext,self.context),
                  'review_state':           safe(self.getWorkflowState,me),
                  }
        return result
        
    def getAuthenticatedMember(self):
        """ Get authenticated member object """
        m_tool = getToolByName(self.context,'portal_membership')
        auth_member = m_tool.getAuthenticatedMember()
        return auth_member
        
    def getWorkflowState(self,object):
        """ Get workflow state for an object """
        wf_tool = getToolByName(self,'portal_workflow')
        return wf_tool.getInfoFor(object,'review_state')

    def getMemberId(self,member):
        """ Get some sort of displayable ID for a member """
        if hasattr(member,'id'):
            return member.id
        else:
            return str(member)
            
            
class AuthenticatedUserProperties(BaseProvider):
	template = 'AuthenticatedUserProperties.pt'

	def getAuthMemberProperties(self):
		""" Get properties for authenticated user """ 
		try:
			properties = self.request['AUTHENTICATED_USER']['mutable_properties']._properties
			msg = None
		except:
			properties = {}
			msg = "Unable to retrieve properties for this member"
		
		return InfoFragment(properties,error_message=msg)