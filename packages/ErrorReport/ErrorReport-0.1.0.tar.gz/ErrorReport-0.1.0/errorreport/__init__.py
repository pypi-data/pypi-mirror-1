"""\
Error report service
"""

import logging
import cgitb
import sys

from bn import AttributeDict, str_dict

log = logging.getLogger(__name__)

class ErrorReportService(object):
    def __init__(
        self,
        to, 
        from_email='error@example.com', 
        from_name='ErrorReportMiddleware',
        subject='Error Report',
    ):
        self.to = to
        self.from_email = from_email
        self.from_name = from_name
        self.subject = subject

    @staticmethod
    def config(flow, name):
        from flows.config import handle_option_error, handle_section_error
        if not flow.config.option.has_key(name):
            raise handle_section_error(flow, name, "'%s.to', '%s.from_email' and '%s.subject'"%(name, name, name))
        from conversionkit import chainConverters, Conversion
        from stringconvert import unicodeToUnicode
        from stringconvert.email import listOfEmails, unicodeToEmail
        from recordconvert import toRecord

        to_unicode = unicodeToUnicode()
        # Error Reporting
        error_mail_converters={
            'subject': to_unicode,
            'to': listOfEmails(),
            'from_email': unicodeToEmail(),
            'from_name': to_unicode,
        }
        error_mail_converter = chainConverters(
            toRecord(
                missing_errors = {'to': "The required option '%s.%%(key)s' is missing"%name},
                empty_errors = {'to': "The option '%s.%%(key)s' cannot be empty"%name},
                converters = error_mail_converters,
            ),
        )
        conversion = Conversion(flow.config.option[name]).perform(error_mail_converter)
        if not conversion.successful:
            handle_option_error(conversion)
        else:
            flow.config[name] = conversion.result
        return flow.config[name]

    @staticmethod
    def create(flow, name, config=None):
        if config is None:
            config = ErrorReportService.config(flow, name)
        return ErrorReportService(**str_dict(config))

    def start(self, flow, key):

        def report(exc_info=None):
            # Use the mail service to send a report
            flow.mail.send(
                display_html(exc_info),
                to=self.to,
                from_email=self.from_email,
                from_name=self.from_name,
                subject=self.subject,
                type='html',
            )

        def display_html(exc_info=None):
            if exc_info is None:
                exc_info = sys.exc_info()
            # Get the traceback information
            return cgitb.html(exc_info)

        flow[key] = AttributeDict()
        flow[key]['report'] = report
        flow[key]['display_html'] = display_html

    def error(self, flow, key):
        original_error = sys.exc_info()
        if not flow.config.app.debug:
            flow[key].report()
            if not hasattr(flow, 'wsgi'):
                log.error('Could not show an error report because the WSGI service is not present')
            else:
                flow.error_document.render(status='500 An error occurred.')
        else:
            if not hasattr(flow, 'wsgi'):
                log.error('Could not show an error report because the WSGI service is not present')
            else:
                flow.wsgi.status = '500 Internal Server Error'
                flow.wsgi.headers = [('Content-type', 'text/html')]
                flow.wsgi.response = [flow[key].display_html()]
        flow.provider['error_handled'] = True

