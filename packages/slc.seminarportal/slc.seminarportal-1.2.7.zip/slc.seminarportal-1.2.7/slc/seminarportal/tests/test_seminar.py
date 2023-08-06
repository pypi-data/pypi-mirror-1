import logging
import random

from zope import event

from DateTime import DateTime

from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.utils import shasattr

from slc.seminarportal.config import names
from slc.seminarportal.config import titles
from slc.seminarportal.config import short_desc
from slc.seminarportal.config import desc
from slc.seminarportal.tests.base import SeminarPortalTestCase

log = logging.getLogger('test_seminar.py')

class TestSeminar(SeminarPortalTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        portal = self.portal
        qi = portal.portal_quickinstaller
        portal.invokeFactory('SPSeminar', 'plone-conference', title="Seminar")
        seminar = getattr(portal, 'plone-conference')
        seminar._renameAfterCreation(check_auto_id=True)
        event.notify(ObjectInitializedEvent(seminar))
        
    def test_subfolders_created(self):
        """ Test for the succesful automatic creation of subfolders.
        """
        portal = self.portal
        seminar = getattr(portal, 'plone-conference')

        # Check that subflolders are created.
        self.failUnlessEqual(shasattr(seminar, 'speakers'), True)
        self.failUnlessEqual(shasattr(seminar, 'speech-venues'), True)


    def test_seminarportal(self):
        """ """
        # XXX: This needs to be refactored.
        portal = self.portal
        seminar = getattr(portal, 'plone-conference')

        # Create Speakers
        speakers_folder = getattr(seminar, 'speakers')
        for surname, firstname in names:
            speaker_id = portal.generateUniqueId('SPSpeaker')
            speakers_folder.invokeFactory('SPSpeaker', 
                                speaker_id,)
            s = getattr(speakers_folder, speaker_id)
            s._renameAfterCreation(check_auto_id=True)
            s.setLastName(surname)
            s.setFirstName(firstname)

        # Create SpeechVenues and Speeches
        speakers = speakers_folder.objectValues()
        num_of_speakers = len(speakers)

        seminar_day = DateTime() + 10
        venues_folder = getattr(seminar, 'speech-venues')
        for i in ['A', 'B']:
            log.info('Creating venue: %s' % i)
            speech_folder_id = 'speech_venue_%s' % i.lower()
            venues_folder.invokeFactory('SPSpeechVenue', speech_folder_id, title='Speech Venue %s' % i, description=short_desc)
            speech_venue = getattr(venues_folder, speech_folder_id)
            for days in [0,1]:
                for title in titles:
                    speech_title = 'Speech: %s' % title
                    sid = portal.generateUniqueId('SPSpeech')
                    start_hour = random.randint(6, 20)
                    end_hour = start_hour + random.randint(0,3)
                    start_date = DateTime('%s %s:%s ' % ((seminar_day+days).Date(), start_hour, random.randint(0,30)))
                    end_date = DateTime('%s %s:%s' % ((seminar_day+days).Date(), end_hour, random.randint(30,59)))

                    speech_venue.invokeFactory('SPSpeech', 
                                        sid, 
                                        title=speech_title, 
                                        description=desc, 
                                        startDate=start_date,
                                        endDate=end_date)
                    speech = getattr(speech_venue, sid)
                    speech._renameAfterCreation(check_auto_id=True)

                    speech_speakers = []
                    for i in range(0,2):
                        rand_index = random.randint(0, num_of_speakers-1)
                        speaker = speakers[rand_index]
                        speech_speakers.append(speaker)
                    speech.setSpeakers(speech_speakers)
                    speech.reindexObject()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSeminar))
    return suite

