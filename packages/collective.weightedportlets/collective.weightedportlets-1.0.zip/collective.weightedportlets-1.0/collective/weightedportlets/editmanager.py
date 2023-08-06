from Products.Five import BrowserView
from collective.weightedportlets import ATTR
import plone.app.portlets.browser
from plone.app.portlets.browser import manage as base
from collective.weightedportlets.utils import ReplacingViewPageTemplateFile

class PortletWeightInfo(BrowserView):

    def portlet_weight(self, renderer, portlet_index):
        assignments = renderer._lazyLoadAssignments(renderer.manager)
        assignment = assignments[portlet_index]
        return getattr(assignment, ATTR, {}).get('weight', 50)

class ManageContextualPortlets(base.ManageContextualPortlets):

    index = ReplacingViewPageTemplateFile(
        module = plone.app.portlets.browser,
        filename = 'templates/edit-manager-macros.pt',
        regexp = r'<span class="managedPortletActions">',
        replacement = """
        <span class="managedPortletActions">
        <input type="text" size="1" class="weight" title="Portlet Weight"
            tal:define="weight_info nocall:context/@@portlet-weight-info"
            tal:attributes="value python:weight_info.portlet_weight(view, repeat['portlet'].index)"
            i18n:domain="collective.weightedportlets"
            i18n:attributes="title"/>
"""
        )
