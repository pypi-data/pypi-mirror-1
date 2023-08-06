import random

from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from Products.CMFPlone import utils
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress

from interfaces import ISpeakerPortlet

class AddForm(base.AddForm):
    form_fields = form.Fields(ISpeakerPortlet)
    
    label = _(u"Add a Speaker Portlet")

    def create(self, data):
        return Assignment(speaker=data.get('speaker'),
                          random=data.get('random'),)


class EditForm(base.EditForm):
    form_fields = form.Fields(ISpeakerPortlet)
    label = _(u"Edit the Speaker Portlet")


class Assignment(base.Assignment):
    implements(ISpeakerPortlet)

    def __init__(self, speaker=None, random=False):
        self.speaker = speaker
        self.random = random 

    @property
    def title(self):
        return _(u"Featured Speaker")


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('speaker.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        portal_state = getMultiAdapter((self.context, self.request), 
                                       name=u'plone_portal_state'
                                       )
        self.portal = portal_state.portal()

    def _render_cachekey(method, self):
        portal_languages = getToolByName(self.context, 'portal_languages')
        preflang = portal_languages.getPreferredLanguage()
        return (preflang)
        
    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.get_speaker() and True or False
        
    def get_speaker(self):
        if self.data.random:
            catalog = getToolByName(self.context, 'portal_catalog')
            brains =  catalog(portal_type='SPSpeaker')
            return brains[random.randint(0, len(brains))].getObject()

        if self.data.speaker:
            try:
                return self.portal.unrestrictedTraverse(self.data.speaker[0])
            except AttributeError:
                pass


