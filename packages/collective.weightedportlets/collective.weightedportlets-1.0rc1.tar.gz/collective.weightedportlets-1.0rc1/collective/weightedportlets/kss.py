from zope.interface import implements

from Acquisition import aq_inner
from persistent.dict import PersistentDict

from plone.app.kss.interfaces import IPloneKSSView

from plone.portlets.utils import unhashPortletInfo
from plone.app.portlets.utils import assignment_mapping_from_key
from plone.app.portlets.browser.kss import PortletManagerKSS as BasePortletManagerKSS
from plone.app.portlets.interfaces import IPortletPermissionChecker

from collective.weightedportlets import ATTR

class PortletManagerKSS(BasePortletManagerKSS):
    """Opertions on portlets done using KSS
    """
    implements(IPloneKSSView)
    
    def change_portlet_weight(self, portlethash, viewname, weight):
        try:
            weight = int(weight)
        except ValueError:
            kss_plone = self.getCommandSet('plone')
            kss_plone.issuePortalMessage('You must enter an integer for the portlet weight.', msgtype='error')
            return self.render()
        
        info = unhashPortletInfo(portlethash)
        assignments = assignment_mapping_from_key(self.context, 
                        info['manager'], info['category'], info['key'])
        
        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()
        
        name = info['name']
        if not hasattr(assignments[name], ATTR):
            setattr(assignments[name], ATTR, PersistentDict())
        getattr(assignments[name], ATTR)['weight'] = weight
        return self._render_column(info, viewname)
