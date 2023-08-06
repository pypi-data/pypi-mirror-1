# Copyright (C) 2008  University of Bern
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Classes for sending messages between components.

This is essentially just an adapter observer pattern.

"""

from collections import defaultdict

__all__ = ('Messenger', 'Publisher', 'Subscriber', 'Hook')


class Messenger(object):
    """Class that subscribers can register themselves to receive messages and 
    publishers can send their messages to."""

    @classmethod
    def default(cls):
        if not hasattr(cls, '_instance') or cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, obj, message):
        self.subscribers[message].append(obj)

    def unsubscribe(self, obj, message=None):
        if message is not None:
            try:
                self.subscribers[message].remove(obj)
            except ValueError:
                pass
            return
        for subscribers in self.subscribers.values():
            try:
                subscribers.remove(obj)
            except ValueError:
                pass

    def notify(self, message, *arg, **kwargs):
        for subscriber in self.subscribers[message]:
            subscriber.notify(message, *arg, **kwargs)


class Publisher(object):
    """Class that publishes messages."""

    def notify(self, message, *arg, **kwargs):
        Messenger.default().notify(message, *args, **kwargs)


class Subscriber(object):
    """Class that subscribes to messages."""

    def subscribe(self, message):
        Messenger.default().register(self, message)

    def notify(self, message, *args, **kwargs):
        raise SubclassResponsibility()


class Hook(Subscriber):
    """A special Subscriber that executes a Command."""

    def __init__(self, command, args=None):
        self.command = command
        self.args = args if args is not None else []

    def notify(self, message, map, *args, **kwargs):
        self.command.execute(**dict([ (x[0], x[1] % map) for x in self.args ]))


