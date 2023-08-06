import datetime

from zope.interface import classProvides, implements
from collective.transmogrifier import interfaces
from collective.transmogrifier.utils import defaultMatcher

import collective.singing.subscribe

class ImportSubscriberSection(object):
    classProvides(interfaces.ISectionBlueprint)
    implements(interfaces.ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context

        self.default_channel_id = options.get('default-channel-id',
                                              'default-channel')
        self.default_composer_id = options.get('default-composer-id', 'html')

        self.channelidkey = defaultMatcher(options, 'channel-id-key',
                                            name, 'channel-id')
        self.composeridkey = defaultMatcher(options, 'composer-id-key',
                                            name, 'composer-id')

        self.emailkey = defaultMatcher(options, 'email-key',
                                       name, key='email')

    def __iter__(self):

        for item in self.previous:
            emailkey = self.emailkey(*item.keys())[0]
            channelidkey = self.channelidkey(*item.keys())[0]
            composeridkey = self.channelidkey(*item.keys())[0]

            # compute the channel id
            if channelidkey is None:
                channel_id = self.default_channel_id
            else:
                channel_id = item[channelidkey]

            # compute the composer id
            if composeridkey is None:
                composer_id = self.default_composer_id
            else:
                composer_id = item[composeridkey]

            # the subscriber's email
            if emailkey is None:
                yield item; continue # not enough infos
            email = u'%s'%item[emailkey]

            # get the channel
            channels = self.context.portal_newsletters.channels
            channel = channels[channel_id]

            # get the subscription tool
            subscriptions = channel.subscriptions

            # check the email doesn't already exists
            if len(subscriptions.query(key=email)) != 0:
                yield item; continue # subscriber already exists

            # add the subscriber
            data = {'email': email}
            metadata = dict(format=composer_id, date=datetime.datetime.now())
            composer = channel.composers[composer_id]
            secret = collective.singing.subscribe.secret(
                        channel, composer, data, self.context.REQUEST)

            subscriptions.add_subscription(channel, secret, data, [], metadata)

            yield item
