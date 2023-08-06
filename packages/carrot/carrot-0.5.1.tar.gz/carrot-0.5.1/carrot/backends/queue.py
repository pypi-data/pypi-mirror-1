"""

    Backend for unit-tests, using the Python :mod:`Queue` module.

"""
from Queue import Queue
from carrot.backends.base import BaseMessage, BaseBackend
import time
import itertools

mqueue = Queue()


class Message(BaseMessage):
    """Message received from the backend.

    See :class:`carrot.backends.base.BaseMessage`.

    """


class Backend(BaseBackend):
    """Backend using the Python :mod:`Queue` library. Usually only
    used while executing unit tests.

    Please not that this backend does not support queues, exchanges
    or routing keys, so *all messages will be sent to all consumers*.

    """

    def get(self, *args, **kwargs):
        """Get the next waiting message from the queue.

        :returns: A :class:`Message` instance, or ``None`` if there is
            no messages waiting.

        """
        if not mqueue.qsize():
            return None
        message_data, content_type, content_encoding = mqueue.get()
        return Message(backend=self, body=message_data,
                       content_type=content_type,
                       content_encoding=content_encoding)

    def consume(self, queue, no_ack, callback, consumer_tag):
        """Go into consume mode."""
        for total_message_count in itertools.count():
            message = self.get()
            if message:
                callback(message.decode(), message)
                yield True
            else:
                time.sleep(0.1)

    def purge(self, queue, **kwargs):
        """Discard all messages in the queue."""
        mqueue = Queue()

    def prepare_message(self, message_data, delivery_mode,
                        content_type, content_encoding, **kwargs):
        """Prepare message for sending."""
        return (message_data, content_type, content_encoding)

    def publish(self, message, exchange, routing_key, **kwargs):
        """Publish a message to the queue."""
        mqueue.put(message)
