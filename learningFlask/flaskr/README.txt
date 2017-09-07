Error Mails

If the application runs in production mode (which it will do on your server) you might not see any log messages.
The reason for that is that Flask by default will just report to the WSGI error stream or stderr
(depending on what’s available). Where this ends up is sometimes hard to find.
Often it’s in your webserver’s log files.

I can pretty much promise you however that if you only use a logfile for the application errors
you will never look at it except for debugging an issue when a user reported it for you.
What you probably want instead is a mail the second the exception happened.
Then you get an alert and you can do something about it.

Flask uses the Python builtin logging system,
and it can actually send you mails for errors which is probably what you want.
Here is how you can configure the Flask logger to send you mails for exceptions:

ADMINS = ['yourname@example.com']
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
                               'server-error@example.com',
                               ADMINS, 'YourApplication Failed')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

So what just happened?
We created a new SMTPHandler that will send mails with the mail server listening on 127.0.0.1 to all the ADMINS
from the address server-error@example.com with the subject “YourApplication Failed”.
If your mail server requires credentials, these can also be provided.
For that check out the documentation for the SMTPHandler.

We also tell the handler to only send errors and more critical messages.
Because we certainly don’t want to get a mail for warnings or other useless logs
that might happen during request handling.

Before you run that in production,
please also look at Controlling the Log Format to put more information into that error mail.
That will save you from a lot of frustration.