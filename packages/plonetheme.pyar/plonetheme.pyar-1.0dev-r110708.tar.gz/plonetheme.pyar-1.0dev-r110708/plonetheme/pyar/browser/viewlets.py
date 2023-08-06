from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import SiteActionsViewlet
from plone.app.layout.viewlets.common import PathBarViewlet
from plone.app.layout.viewlets.common import PersonalBarViewlet

class PyArSiteActionsViewlet(SiteActionsViewlet):
    index = ViewPageTemplateFile('templates/site_actions.pt')

class PyArPathBar(PathBarViewlet):
    render = ViewPageTemplateFile("templates/path_bar.pt")

class PyArPersonalBarViewlet(PersonalBarViewlet):
    index = ViewPageTemplateFile('templates/personal_bar.pt')
