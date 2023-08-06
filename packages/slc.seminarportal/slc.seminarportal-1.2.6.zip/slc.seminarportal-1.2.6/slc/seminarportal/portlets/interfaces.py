from zope import schema
from zope.interface import Interface

from plone.portlets.interfaces import IPortletDataProvider

from Products.CMFPlone import PloneMessageFactory as _

class ISpeakerPortlet(IPortletDataProvider):
    """Interface for portlet to display seminar speakers
    """
    speaker = schema.List(title=_(u"Choose a speaker"),
                        description=u'Make sure you choose only one speaker',
                        required=False,
                        max_length=1,
                        value_type=schema.Choice(
                            vocabulary="slc.seminarportal.vocabularies.speakers")
                        )
                         
    random = schema.Bool(title=_(u'or click here to display a random speaker'),
                         required=False,
                         default=False)


    def get_speaker():
        """ """

class ISpeechesPortlet(IPortletDataProvider):
    """Interface for portlet to display seminar speeches 
    """
    count = schema.Int( 
                    title=_(u'How many speeches should be displayed.'),
                    required=True,
                    default=5)

    def get_speaker():
        """ """

class ISearchPortlet(Interface):
    """Interface for portlet to search inside seminars
    """

