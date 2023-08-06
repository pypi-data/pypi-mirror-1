
from plone.app.layout.viewlets.content import DocumentActionsViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
class wwpdocument_actions(DocumentActionsViewlet):
    render = ViewPageTemplateFile("templates/document_actions.pt")    
    