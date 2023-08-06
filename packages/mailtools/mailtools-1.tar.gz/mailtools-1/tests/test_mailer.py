"""
Test suite for mailtools.mailer
"""

import sys
import logging
import Queue
import time

from email import message_from_string
from itertools import count
from smtplib import SMTPResponseException

from nose.tools import assert_equal

from mailtools.mailer import SMTPTransport
from mailtools.mailer import Mailer
from mailtools.mailer import ThreadedMailer

class CallbackHandler(logging.Handler):
    """
    Handler that allows a test case to intercept messages logged by the mailer
    object
    """

    def __init__(self,
                 callback=None,
                 debug_callback = None,
                 info_callback = None,
                 warn_callback = None,
                 error_callback = None,
                 critical_callback = None,
        ):

        """
        Initialize the Handler. If ``callback`` is set, it will be called with
        all records logged. If any of the other ``*_callback`` arguments are
        given, those callbacks will be triggered on reciept of a log record of
        exactly that level.
        """
        logging.Handler.__init__(self)
        self.callback = callback
        self.level_callbacks = {
            logging.DEBUG: debug_callback,
            logging.INFO: info_callback,
            logging.WARNING: warn_callback,
            logging.ERROR: error_callback,
            logging.CRITICAL: critical_callback,
        }

    def emit(self, record):
        """
        Implementation of ``logging.Handler.emit``
        """
        if self.callback is not None:
            self.callback(record)
        cb = self.level_callbacks[record.levelno]
        if cb is not None:
            cb(record)

class TestTransport(SMTPTransport):

    def __init__(self, *args, **kwargs):
        super(TestTransport, self).__init__('127.0.0.1')
        self.sent = Queue.Queue()
        self.log = []
        self.debug_log = []
        self.info_log = []
        self.warning_log = []
        self.error_log = []
        self.critical_log = []

        self.logger = logging.getLogger('%d-0x%x' % (time.time(), id(self)))
        self.logger.addHandler(CallbackHandler(
            callback = self.log.append,
            debug_callback = self.debug_log.append,
            info_callback = self.info_log.append,
            warn_callback = self.warning_log.append,
            error_callback = self.error_log.append,
            critical_callback = self.critical_log.append,
        ))

    def send_many(self, messages):
        for m in messages:
            self.sent.put(m)
        return []

def test_sending_many_messages_returns_errors():

    class TestTransportWithError(TestTransport):
        """
        Will return a 500 delivery failure message when called
        """
        def send_many(self, messages):

            try:
                raise SMTPResponseException(500, 'permanent failure')
            except Exception:
                exc_info = sys.exc_info()
                return [ (exc_info, message) for message in messages ]

    transport = TestTransportWithError()
    mailer = Mailer(transport=transport, logger=transport.logger)
    mailer._send_many([('fromaddr', ['toaddr'], 'message')])

    exc_info = transport.error_log[0].args[0]
    assert "permanent failure" in str(exc_info[1])

def test_threaded_mailer_sends_a_message():

    sent = Queue.Queue()

    transport = TestTransport()
    mailer = ThreadedMailer(Mailer(transport=transport))
    message = ('fromaddr', ['toaddr'], 'message')
    mailer.send(*message)
    assert_equal(message, transport.sent.get(timeout=1))

def test_threaded_mailer_retries_a_temporary_failure_at_correct_interval():

    class TestTransportWithRetry(TestTransport):
        """
        Will return a 400 temporary failure message the first time called,
        thereafter simulate a successful delivery
        """

        def __init__(self):
            super(TestTransportWithRetry, self).__init__()
            self.called_at = []

        def send_many(self, messages):
            self.called_at.append(time.time())
            if len(self.called_at) == 1:
                try:
                    raise SMTPResponseException(400, 'temporary failure')
                except Exception:
                    exc_info = sys.exc_info()
                    return [ (exc_info, message) for message in messages ]

            self.sent.put(messages)
            return []

    transport = TestTransportWithRetry()
    mailer = ThreadedMailer(Mailer(transport=transport, logger=transport.logger))
    mailer.retry_period = 0.5

    message = ('fromaddr', ['toaddr'], 'message')
    mailer.send(*message)
    assert_equal([message], transport.sent.get(timeout=2))

    assert len(transport.called_at) == 2, "transport was not called exactly twice"
    assert transport.called_at[1] - transport.called_at[0] >= mailer.retry_period, "retried too soon"

    exc_info = transport.error_log[0].args[0]
    assert "temporary failure" in str(exc_info[1]), "initial failure not logged"


def test_threaded_mailer_doesnt_retry_a_permanent_failure():

    class TestTransportWithError(TestTransport):

        def __init__(self):
            super(TestTransportWithError, self).__init__()
            self.called_at = []

        def send_many(self, messages):
            self.called_at.append(time.time())
            try:
                raise SMTPResponseException(500, 'permanent error')
            except Exception:
                exc_info = sys.exc_info()
                return [ (exc_info, message) for message in messages ]

    transport = TestTransportWithError()
    mailer = ThreadedMailer(Mailer(transport=transport, logger=transport.logger))
    mailer.retry_period = 0.5

    message = ('fromaddr', ['toaddr'], 'message')
    mailer.send(*message)
    try:
        transport.sent.get(timeout=2)
    except Queue.Empty:
        pass
    else:
        raise AssertionError("Message should not have been sent")

    assert len(transport.called_at) == 1, "transport was not called exactly once"


def test_threaded_mailer_sends_multiple_messages():

    transport = TestTransport()
    mailer = ThreadedMailer(Mailer(transport=transport, logger=transport.logger))

    messages = [
        ('fromaddr', ['toaddr'], 'message-%d' % ix)
        for ix in range(20)
    ]
    expected = set('message-%d' % ix for ix in range(20))

    for m in messages:
        mailer.send(*m)
    while expected:
        try:
            fromaddr, toaddrs, message = transport.sent.get(timeout=2)
            expected.remove(message)
        except Queue.Empty:
            raise AssertionError("Message expected")

def test_threaded_mailer_sends_in_batches():

    class TestTransportWithBatchNumber(TestTransport):

        def __init__(self):
            super(TestTransportWithBatchNumber, self).__init__()
            self.batchcounter = count()

        def send_many(self, messages):
            b = self.batchcounter.next()
            for m in messages:
                self.sent.put((b, m))
            return []

    transport = TestTransportWithBatchNumber()
    mailer = ThreadedMailer(Mailer(transport=transport, logger=transport.logger))
    mailer.batchsize = 2

    messages = [
        ('fromaddr', ['toaddr'], 'm1'),
        ('fromaddr', ['toaddr'], 'm2'),
        ('fromaddr', ['toaddr'], 'm3'),
        ('fromaddr', ['toaddr'], 'm4'),
        ('fromaddr', ['toaddr'], 'm5'),
    ]
    expected = [
        (0, 'm1'),
        (0, 'm2'),
        (1, 'm3'),
        (1, 'm4'),
        (2, 'm5'),
    ]

    for m in messages:
        mailer.send(*m)
    while expected:
        try:
            batch, (fromaddr, toaddrs, message) = transport.sent.get(timeout=2)
            expected.remove((batch, message))
        except Queue.Empty:
            raise AssertionError("Message expected")

def test_send_plain_sets_text_plain_content_type():

    transport = TestTransport()
    mailer = Mailer(transport=transport)
    mailer.send_plain(u'me@mydomain', [u'you@yourdomain'], u'subject line', u'Hi buddy!')
    env_from, env_to, message = transport.sent.get()

    assert_equal(message_from_string(message)['Content-Type'], 'text/plain; charset=UTF-8')


def test_send_html_sets_text_html_content_type():

    transport = TestTransport()
    mailer = Mailer(transport=transport)
    mailer.send_html(u'me@mydomain', [u'you@yourdomain'], u'subject line', u'Hi buddy!')
    env_from, env_to, message = transport.sent.get()

    assert_equal(message_from_string(message)['Content-Type'], 'text/html; charset=UTF-8')




