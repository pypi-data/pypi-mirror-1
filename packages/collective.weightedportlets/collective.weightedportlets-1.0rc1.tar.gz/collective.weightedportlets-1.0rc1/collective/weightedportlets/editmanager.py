from Products.Five import BrowserView
from collective.weightedportlets import ATTR

class PortletWeightInfo(BrowserView):
    
    def portlet_weight(self, renderer, portlet_index):
        assignments = renderer._lazyLoadAssignments(renderer.manager)
        assignment = assignments[portlet_index]
        return getattr(assignment, ATTR, {}).get('weight', 50)
