from plone.app.layout.viewlets.common import SearchBoxViewlet as CustomSearchBoxViewlet

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class SearchBoxViewlet(CustomSearchBoxViewlet):
    render = ViewPageTemplateFile('searchbox.pt')

