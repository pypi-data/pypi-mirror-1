import unittest
from zope.component import provideUtility
from zope.interface import classProvides, implements
from zope.testing import doctest
from collective.transmogrifier.interfaces import ISectionBlueprint, ISection
from collective.transmogrifier.tests import tearDown
from collective.transmogrifier.sections.tests import sectionsSetUp
from collective.transmogrifier.sections.tests import SampleSource
from Products.Five import zcml

# Doctest support

ctSectionsSetup = sectionsSetUp
def sectionsSetUp(test):
    ctSectionsSetup(test)
    import plone.app.transmogrifier
    import collective.blueprint.dancing
    zcml.load_config('configure.zcml', plone.app.transmogrifier)
    zcml.load_config('configure.zcml', collective.blueprint.dancing)

def importSubscriberSetup(test):
    sectionsSetUp(test)

    from Products.Archetypes.interfaces import IBaseObject
    import collective.singing.subscribe

    # dummy classes for S&D

    def mocksecret(*arg, **kwargs): return 'secret'
    collective.singing.subscribe.secret = mocksecret

    class MockComposer(object):

        def __init__(self, id):
            self.id = id

    class MockComposers(object):

        def __getitem__(self, key):
            return MockComposer(key)

    class MockChannel(object):

        def __init__(self, id, portal):
            self.portal = portal
            self.id = id

        @property
        def subscriptions(self):
            return self.portal

        @property
        def composers(self):
            return MockComposers()

    class MockChannels(object):

        def __init__(self, portal):
            self.portal = portal

        def __getitem__(self, key):
            return MockChannel(key, self.portal)

    class MockPortal(object):
        implements(IBaseObject)

        subscribers = ()

        # dummy methods for S&D

        @property
        def portal_newsletters(self): return self

        @property
        def channels(self): return MockChannels(self)

        @property
        def subscriptions(self): return self

        def query(self, key=''):
            if key == 'existing@email.com':
                return ['existing@email.com']
            else:
                return []

        @property
        def REQUEST(self): return {}

        def add_subscription(self, channel, secret,
                             data, composer_data, metadata):
            self.subscribers += (('%s -channel:%s - composer:%s' % (
                                                        data['email'],
                                                        channel.id,
                                                        metadata['format'])),)

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class ImportSubscriberSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(ImportSubscriberSource, self).__init__(*args, **kw)
            self.sample = (
                # will be added
                dict(_email ='foo@foo.com'),
                # will be added
                dict(_email ='bar@bar.com'),
                # existing subscriber, will be skipped
                dict(_email ='existing@email.com'),
            )
    provideUtility(ImportSubscriberSource,
        name=u'collective.blueprint.dancing.tests.importsubscribersource')

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'importsubscriber.txt',
            setUp=importSubscriberSetup, tearDown=tearDown),
    ))
