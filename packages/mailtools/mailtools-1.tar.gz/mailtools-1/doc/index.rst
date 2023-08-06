mailtools
----------

Writing a web application? Want to send some emails from it? Mailtools can
help!

 - Simple API for sending plain text messages, HTML and messages with
   attachments.

 - ``ThreadedMailer`` sends emails in the background and returns control 
   to your application immediately, even when talking to slow remote servers.

 - Temporary sending failures are automatically retried.

 - Running your application in test mode? The ``RedirectMessages`` wrapper
   routes emails to a test address and not to live email addresses.

.. toctree::
        :maxdepth: 2

        api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Sample usage
------------

Creating a simple SMTP mailer:

.. testsetup:: *

        from mailtools.mailer import TestMailer, ThreadedMailer, SMTPMailer


.. testcode::

        mailer = SMTPMailer('127.0.0.1')

This mailer will block until messages are sent and won't retry failures. Use
``ThreadedMailer`` to fix this:

.. testcode::

        mailer = ThreadedMailer(SMTPMailer('127.0.0.1'))

Sending a plain text message:


.. testcode::
        :hide:

        mailer = TestMailer()
        inbox = mailer.subscribe()

.. testcode::

        message = u'This is a plain text message to demonstrate how easy it is to send an email'
        mailer.send_plain(
                u'sender@example.com',
                [u'recipient@example.com'],
                u'hi',
                message
        )

.. doctest::
        :hide:

        >>> inbox
        [(u'sender@example.com', [u'recipient@example.com'], '...\nContent-Type: text/plain; charset=UTF-8...\nTo: recipient@example.com\nSubject: hi\nFrom: sender@example.com\n...\n\nThis=20is=20a=20plain=20text=20message=20to=20demonstrate=20how=20easy=20it=\n=20is=20to=20send=20an=20email')]


The ``message`` body and all headers must be unicode strings, or you'll get an
error. ``mailtools`` automatically handles output encoding so that unicode
characters are handled correctly wherever they appear.

Sending an HTML message:

.. testcode::

        message = u'<html><body><blink>Look! HTML!</blink></body></html>'
        mailer.send_html(
                u'sender@example.com',
                [u'recipient@example.com'],
                u'hi',
                message
        )

.. doctest::
        :hide:

        >>> inbox[-1]
        (u'sender@example.com', [u'recipient@example.com'], '...\nContent-Type: text/html; charset=UTF-8...\nTo: recipient@example.com\nSubject: hi\nFrom: sender@example.com\n...\n\n<html><body><blink>Look!=20HTML!</blink></body></html>')

Adding attachments:

        
.. testcode::

        message = u'index.rst is attached to this message'
        mailer.send_plain(
                u'sender@example.com',
                [u'recipient@example.com'],
                u'hi',
                message,
                attachments=['index.rst']
        )


.. doctest::
        :hide:

        >>> inbox[-1]
        (u'sender@example.com', [u'recipient@example.com'], 'Content-Type: multipart/mixed;...To: recipient@example.com\nSubject: hi\nFrom: sender@example.com\n...\n\nindex.rst=20is=20attached=20to=20this=20message...Content-Disposition: attachment; filename="index.rst"...')

