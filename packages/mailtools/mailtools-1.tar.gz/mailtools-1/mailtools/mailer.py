"""
Tools for sending email.

``MailTransport`` subclasses wrap mail transports (currently only SMTP is
supported)

``Mailer`` subclasses provide convenient APIs for sending messages

"""
import email.message
import itertools
import logging
import Queue
import smtplib
import sys
import threading
import time
import weakref


from email.mime.text import MIMEText
from functools import partial
from smtplib import SMTPResponseException

from mailtools.utils import \
        add_attachments, extract_recipients, \
        make_header, split_headers, strip_name

__all__ = [
    'SMTPTransport',
    'Mailer',
    'SMTPMailer',
    'ThreadedMailer',
    'RedirectMessages',
    'CopyMessages',
]


class MailTransport(object):
    """
    ``MailTransport`` objects are responsible for sending a list of messages to
    the underlying transport.
    """

    def send_many(self, messages):
        """
        Send a list of messages in the format::

            ``(<envelope sender>, <envelope recipient>, <message string>)``
        """
        raise NotImplementedError

    @staticmethod
    def is_retryable(exception):
        """
        Return ``True`` if the given exception indicates a temporary failure
        """
        raise NotImplementedError

class SMTPTransport(MailTransport):
    """
    Implementations of ``MailTransport`` that uses regular SMTP via Python's
    ``smtplib``
    """

    def __init__(self, host, port=25, username=None, password=None):
        """
        Configure the SMTPTransport with ``host``, ``port``, and optionally a
        ``username`` and ``password``.

        host
            SMTP server to send emails through.

        port
            TCP port number to use when communicating with the server.

        username
            Username to provide when communicating with the server, if one is required.

        password
            Password to provide when communicating with the server, if one is required.


        """
        super(SMTPTransport, self).__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    @staticmethod
    def is_retryable(exception):
        """
        Return ``True`` if the given exception indicates a temporary failure
        """
        return isinstance(exception, SMTPResponseException) and str(exception.smtp_code)[0] == '4'

    def send_many(self, messages):
        """
        Send the given list of messages via SMTP.

        messages
            List in the form ``[(envelope_sender, [envelope_recipients], message)]``.
            The message component of each item must be the raw message as a
            byte string.
        """

        try:
            smtp = smtplib.SMTP(self.host, self.port)
            if self.username:
                smtp.login(self.username, self.password)
        except Exception:
            exc_info = sys.exc_info()
            return [ (exc_info, message) for message in messages ]

        errors = []
        try:
            for fromaddr, toaddrs, message in messages:
                try:
                    smtp.sendmail(fromaddr, toaddrs, message)
                except Exception:
                    errors.append((sys.exc_info(), (fromaddr, toaddrs, message)))
        finally:
            smtp.quit()
        return errors

class BaseMailer(object):
    """
    Base class for mailers.

    Exposes various ``send`` methods, which ultimately call ``_send_many``.
    Subclasses should implement ``_send_many``.
    """

    transport = None
    log_messages = False
    log_file = None

    def __init__(self, log_messages=True, log_file=None, logger=None):
        """
        Configure ``BaseMailer`` instance.

        log_messages
            If true, emails will be recorded through python's logging system.

        log_file
            If set, the logging system will be configured to log to the named
            path. Useful for debugging, or simply to keep a complete record of
            messages sent from your site.

        logger
            Logger to be used, if not supplied a logger named
            ``mailtools.mailer`` will be used
        """

        if logger is None:
            logger = logging.getLogger("mailtools.mailer")
            logger.setLevel(logging.INFO)
        self.logger = logger

        self.log_messages = log_messages

        if log_file is not None:
            mailer_log = logging.FileHandler(log_file)
            mailer_log.setLevel(logging.INFO)
            fmt = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
            mailer_log.setFormatter(logging.Formatter(fmt))
            self.logger.addHandler(mailer_log)


    def _send_many(self, messages):
        """
        Send a list of messages and return a list of
        ``[(exc_info, message), ... ]`` for any errors encountered
        """
        raise NotImplementedError

    def send(self, envelope_sender, envelope_recipients, message):
        """
        Send a message with the given envelope sender and recipients.

        envelope_sender
            Envelope sender address to use

        envelope_recipients
            List of envelope recipient addresses

        message
            Either a byte string or a ``email.message.Message`` object

            If an ``email.message.Message`` object, this will add Message-Id
            and Date headers if not already present.
        """
        if isinstance(message, email.message.Message):

            if 'message-id' not in message:
                message['Message-ID'] = email.utils.make_msgid()

            if 'date' not in message:
                message['Date'] = email.utils.formatdate(localtime=True)

            message = message.as_string()

        errors = self._send_many([(envelope_sender, envelope_recipients, message)])
        if errors:
            exc = errors[0][0]
            raise exc[0], exc[1], exc[2]

    def send_text(
        self,
        from_addr,
        to_addrs,
        subject,
        payload_text,
        subtype,
        attachments=None,
        **headers
    ):
        """
        Send a message with a ``text/*`` payload::

            >>> mailer = TestMailer()
            >>> mailer.send_text(
            ...     u'sender@example.com',
            ...     [u'recipient@example.com'],
            ...     u'hello',
            ...     u'Hello there!',
            ...     'plain'
            ... )

        from_addr
            From address to be used. This will be added as a header to the
            message and also used as the envelope sender. The sender's name may
            be included, both ``'me@mydomain'`` and  ``'Me <me@mydomain>'`` are
            valid.

        to_addrs
            List of recipient addresses.
            The recipient's names may be included, both ``['you@yourdomain']``
            and  ``['You <you@yourdomain>']`` are valid.

        subject
            unicode string to be used as subject line

        payload_text
            unicode string to be used as message payload (body)

        subtype
            MIME subtype, usually one of ``plain`` or ``html``

        attachments
            Optional: list of attachments in any of the following formats:

                - the path of a file to attach
                - a tuple of: ``(<string>, filename)``
                - a tuple of: ``(<file-like object>, filename)``
                - any mime object

        **headers
            Other headers may be specied as keyword arguments
        """
        if not isinstance(payload_text, unicode):
            raise ValueError("Expected unicode payload")

        message = MIMEText('text', subtype)
        message.set_payload(payload_text.encode('UTF-8').encode('quopri'))

        del message['Content-Type']
        del message['Content-Transfer-Encoding']
        message['Content-Type'] = 'text/%s; charset=UTF-8' % (subtype,)
        message['Content-Transfer-Encoding'] = 'quoted-printable'

        if isinstance(to_addrs, basestring):
            to_addrs = to_addrs.split(',')
        to_addrs = list(to_addrs)

        message = add_attachments(message, attachments)
        message['To'] = make_header(','.join(to_addrs))
        message['Subject'] = make_header(subject)
        message['From'] = make_header(from_addr)

        for name, value in headers.items():
            while name[-1] == '_':
                name = name[:-1]
            message[name.replace('_', '-').title()] = make_header(value)

        envelope_recipients = extract_recipients(message)
        envelope_sender = strip_name(from_addr)
        del message['Bcc']

        return self.send(envelope_sender, envelope_recipients, message)

    def send_plain(self, *args, **kwargs):
        """
        Sends a message of type ``text/plain``. See  ``send_text`` for a full
        description of this function's arguments.
        """
        return self.send_text(subtype='plain', *args, **kwargs)

    def send_html(self, *args, **kwargs):
        """
        Sends a message of type ``text/html``. See  ``send_text`` for a full
        description of this function's arguments.
        """
        return self.send_text(subtype='html', *args, **kwargs)

    def send_text_with_headers(self, payload_text, subtype, attachments=None, **extra_headers):
        r"""
        Like ``send_text``, but read the ``from``, ``to`` and ``subject``
        headers from the message body::

            >>> mailer = TestMailer()
            >>> mailer.send_text_with_headers(
            ...     u"From: me@mydomain\n"
            ...     u"To: 'You <you@yourdomain>'\n"
            ...     u"Subject: hello\n"
            ...     u"\n"
            ...     u"Hello there!\n",
            ...     subtype='plain'
            ... )
            >>>

        """
        headers, payload_text = split_headers(payload_text)
        import logging; logging.warn('%r, %r', headers, payload_text)
        headers = dict((k.lower(), v) for k, v in headers)
        headers.update((k.lower(), v) for k, v in extra_headers.items())

        from_addr = headers.pop('from')
        to_addrs = headers.pop('to').split(',')
        subject = headers.pop('subject', u'')

        return self.send_text(
            from_addr,
            to_addrs,
            subject,
            payload_text,
            subtype,
            attachments=attachments,
            **headers
        )


class Mailer(BaseMailer):
    """
    ``Mailer`` exposes a public API for sending email messages. Messages are
    sent synchronously and failures are not retried.
    """

    def __init__(self, transport, log_messages=True, log_file=None, logger=None):
        """
        transport
            Instance of ``MailTransport`` that will be used to actually send
            the messages

        log_messages
            If true, emails will be recorded through python's logging system.

        log_file
            If set, the logging system will be configured to log to the named
            path. Useful for debugging, or simply to keep a complete record of
            messages sent from your site.

        """
        super(Mailer, self).__init__(log_messages, log_file, logger)
        self.transport = transport

    def send(self, envelope_sender, envelope_recipients, message):
        """
        Send a message with the given envelope sender and recipients.

        envelope_sender
            Envelope sender address to use

        envelope_recipients
            List of envelope recipient addresses

        message
            Either a byte string or a ``email.message.Message`` object

            If an ``email.message.Message`` object, this will add Message-Id
            and Date headers if not already present.
        """

        if self.log_messages:
            self.logger.info(
                "Sending message: \n\nFrom: %s\nTo: %r\n\n%s",
                envelope_sender, envelope_recipients, message
            )

        return super(Mailer, self).send(
            envelope_sender,
            envelope_recipients,
            message
        )


    def _send_many(self, messages):
        """
        Send multiple messages in a single batch (eg a single SMTP session).
        Return a list of errors encountered (if any) in the format::

            [
                (exc_info, (fromaddr, toaddrs, message)),
                ...
            ]
        """
        errors = self.transport.send_many(messages)
        if errors:
            for exc_info, message in errors:
                self.logger.error("Exception while sending message %r", exc_info)
                self.logger.info("Message %s", message)
        return errors

class ThreadedMailer(BaseMailer):
    """
    ``ThreadedMailer`` wraps a mailer to provide background sending of messages
    in a second thread and automatic retrying of temporary failures.

    Usage::

        >>> mailer = ThreadedMailer(SMTPMailer('127.0.0.1'))
        >>>
    """

    # Try sending ``batchsize`` messages per smtp session
    batchsize = 10

    # retry unsendable messages for ``retry_period`` seconds
    retry_period = 600

    # maximum number of attempts to deliver a message before discarding it
    max_attempts = 100

    # maximum size of retry queue
    max_queue_size = 100

    def __init__(self, mailer):
        """
        mailer
            The ``Mailer`` instance that will be used to route messages
        """
        super(ThreadedMailer, self).__init__()

        self.mailer = mailer

        # Queue of messages to be sent
        self.queue = Queue.Queue()

        # Messages that failed and can be retried Entries in this queue are
        # tuples of ``(last_attempt_time, notries, message)``.
        # PriorityQueue (2.6+) ensures that the least recently attempted
        # delivery will be retrieved first.
        if getattr(Queue, 'PriorityQueue', None):
            requeue_class = Queue.PriorityQueue
        else:
            requeue_class = Queue.Queue
        self.requeue = requeue_class()

        self._start_listener()
        self._start_retry_processor()

    def send(self, envelope_sender, envelope_recipients, message):
        """
        Queue a single message for sending and return immediately

        ``envelope_sender``
            Envelope sender email address

        ``envelope_recipients``
            List of envelope recipient email addresses
        """
        if self.mailer.log_messages:
            self.mailer.logger.info(
                "Queuing message: \n\nFrom: %s\nTo: %s\n\n%s",
                envelope_sender, envelope_recipients, message
            )
        super(ThreadedMailer, self).send(
            envelope_sender,
            envelope_recipients,
            message,
        )

    def _send_many(self, messages):
        """
        Put ``messages`` into the queue.
        """
        for message in messages:
            self.queue.put(message)

    def _start_listener(self):
        """
        Start a thread to listen for messages entering the queue
        (``self.queue``) and pass them on to a queue processor.

        The thread started by this method is a daemon thread and will not block
        process exit.
        """

        def listener():
            """
            Target function for the listener thread - wait for items to appear
            on ``self.queue`` then hand off to a queue processor thread.
            """

            while True:
                message = self.queue.get(block=True)
                queue_processor = self._start_queue_processor(message)
                queue_processor.join()

        thread = threading.Thread(target=listener)
        thread.daemon = True
        thread.start()
        return thread

    def _start_queue_processor(self, firstmessage):
        """
        Start a thread to process any messages currently on the queue, up to a
        maximum of ``batchsize``, and then finish.

        The thread started by this method is not a daemon thread and will block
        process exit until sending is complete.
        """

        def processor():
            """
            Target function for the queue processor thread. Read at most
            ``batchsize`` messages from ``self.queue`` and send them
            immediately.
            """

            # Duration to wait for a new message to appear in the queue before
            # giving up and sending anyway.
            block_timeout = 0.8

            to_send = [firstmessage]
            for count in xrange(self.batchsize - 1):
                try:
                    to_send.append(self.queue.get(timeout=block_timeout))
                except Queue.Empty:
                    break

            errors = self.mailer._send_many(to_send)
            for exc_info, message in errors:
                if self.mailer.transport.is_retryable(exc_info[1]):
                    self.requeue.put((time.time(), 0, message))

        thread = threading.Thread(target=processor)
        thread.daemon = False
        thread.start()
        return thread

    def _start_retry_processor(self):
        """
        Start a thread to watch for any new messages entering the retry queue
        and periodically retry sending.

        The thread started by this method is a daemon thread and will not block
        process exit.
        """

        def retry_processor():
            """
            Target function for the retry thread: watch ``self.requeue`` and
            periodically retry sending of previously failed messages.
            """
            while True:
                last_attempt, notries, message = self.requeue.get(block=True)

                if notries > self.max_attempts:
                    continue

                time_till_retry = (last_attempt + self.retry_period) - time.time()
                if time_till_retry > 0:
                    self.requeue.put((last_attempt, notries, message))
                    time.sleep(time_till_retry)
                    continue

                errors = self.mailer._send_many([message])
                for exc_info, message in errors:
                    if self.mailer.transport.is_retryable(exc_info[1]):
                        self.requeue.put((time.time(), notries+1, message))

        thread = threading.Thread(target=retry_processor)
        thread.daemon = True
        thread.start()
        return thread

class SMTPMailer(Mailer):
    """
    Convenience subclass of ``Mailer`` that uses an SMTP transport
    """
    def __init__(self,
                 host, port=25,
                 username=None, password=None,
                 log_messages=True, log_file=None,
                 transport_class=SMTPTransport,
                 logger=None
    ):
        """
        host
            SMTP server hostname

        port
            SMTP server port number

        username
            Optional: used to login to the SMTP service

        password
            Optional: used to login to the SMTP service

        log_messages
            As ``Mailer.log_messages``

        log_file
            As ``Mailer.log_file``

        transport_class
            Transport class to use

        """

        super(SMTPMailer, self).__init__(
            transport_class(host, port, username, password),
            log_messages, log_file, logger
        )


class RedirectMessages(BaseMailer):
    """
    Redirects all email to a single address.

    Usage::

        >>> mailer = RedirectMessages(['test@example.com'], Mailer('127.0.0.1', 25))
    """
    def __init__(self, redirect_to, mailer):
        """
        redirect_to
            email address to redirect messages to

        mailer
            instance of ``mailtools.mailer.Mailer`` to pass messages on to for sending
        """
        super(RedirectMessages, self).__init__()
        if isinstance(redirect_to, basestring):
            redirect_to = [redirect_to]
        self.redirect_to = redirect_to
        self.mailer = mailer

    def _send_many(self, messages):
        """
        Call ``self.mailer.send`` replacing the envelope recipients with
        the redirected address
        """
        for env_sender, env_recipient, message in messages:
            self.mailer.send(env_sender, self.redirect_to, message)

class CopyMessages(BaseMailer):
    """
    BCCs all email to a second address.

    Usage::

        >>> mailer = CopyMessages(['test@example.com'], Mailer('127.0.0.1', 25))
    """
    def __init__(self, copy_to, mailer):
        """
        copy_to
            email address to copy messages to
        mailer
            instance of ``mailtools.mailer.Mailer`` to pass messages on to for
            sending
        """
        super(CopyMessages, self).__init__()
        if isinstance(copy_to, basestring):
            copy_to = [copy_to]
        self.copy_to = copy_to
        self.mailer = mailer

    def _send_many(self, messages):
        """
        Call ``self.mailer.send`` adding the copy_to addresses to the
        envelope recipients
        """
        for env_sender, env_recipient, message in messages:
            self.mailer.send(
                env_sender,
                list(self.copy_to) + list(env_recipient),
                message
            )

class TestMailer(BaseMailer):
    r"""
    A dummy mailer object, useful when writing test code

    Usage::

        >>> def function_that_sends_mail(mailer):
        ...     mailer.send('me@example.com', ['you@example.com'], 'Subject: hello\n\nhi there!')
        ...
        >>> mailer = TestMailer()
        >>> inbox = mailer.subscribe()
        >>> function_that_sends_mail(mailer)
        >>> inbox[0]
        ('me@example.com', ['you@example.com'], 'Subject: hello\n\nhi there!')
    """


    class Inbox(list):

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, exc_traceback):
            pass

    def __init__(self):
        """
        Initialize the new ``mailtools.mailer.TestMailer`` instance.
        """

        super(TestMailer, self).__init__()
        self.subscribers = weakref.WeakValueDictionary()
        self._subscriber_seq = itertools.count()

    def _send_many(self, messages):
        """
        Send the given messages
        """
        for inbox in self.subscribers.values():
            inbox.extend(messages)

    def subscribe(self):
        """
        Return a new empty ``Inbox`` object subscribed to the mailer.
        """
        inbox = self.Inbox()
        self.subscribers[self._subscriber_seq.next()] = inbox
        return inbox


