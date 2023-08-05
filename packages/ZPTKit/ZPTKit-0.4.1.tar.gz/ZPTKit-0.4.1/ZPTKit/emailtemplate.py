##########################################################################
#
# Copyright (c) 2005 Imaginary Landscape LLC and Contributors.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##########################################################################

__all__ = ['EmailTemplate', 'send_mail']

from templatetools import FilePageTemplate
import cgi
import re
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import smtplib
import htmlrender

class EmailTemplate(FilePageTemplate):
    """
    A system for templates that are intended to be sent as emails.

    Templates can contain markup like:

    <header name="subject" tal:content="options/subject">subject</header>

    and so on, to define headers.  When rendering a template, an email
    object will be returned (from the email module in the standard
    library).

    Templates will be rendered twice, once for HTML and once for a text
    version.  The template may test for the variable "email_html" and
    "html_text" to see which version is being created.  The text version
    will be converted from HTML to text via the htmlrender module.

    The send_mail() module will load, render, and send the email in
    one step.
    """

    def __call__(self, context=None, *args, **kw):
        if context is None:
            context = {}
        else:
            context = context.copy()
        include_html = popdefault(kw, 'include_html', True)
        include_text = popdefault(kw, 'include_text', True)
        assert include_html or include_text, (
            "You must have at least one of include_html or "
            "include_text as True")
        html = text = None
        if include_html:
            context['email_html'] = True
            context['email_text'] = False
            html = FilePageTemplate.__call__(
                self, context=context, *args, **kw)
        if include_text:
            context['email_html'] = False
            context['email_text'] = True
            text = FilePageTemplate.__call__(
                self, context=context, *args, **kw)
        if html:
            headers, html = self.parse_headers(html)
        if text:
            headers, text = self.parse_headers(text)
            text = htmlrender.render(text)

        return self.create_message(headers, html, text)

    def create_message(self, headers, html, text):
        msg = MIMEMultipart()
        for name, value in headers:
            msg[name] = value
        msg.set_type('multipart/alternative')
        msg.preamble = ''
        msg.epilogue = ''
        if text:
            text_msg = MIMEText(text)
            text_msg.set_type('text/plain')
            text_msg.set_param('charset', 'UTF-8')
            msg.attach(text_msg)
        if html:
            html_msg = MIMEText(html)
            html_msg.set_type('text/html')
            html_msg.set_param('charset', 'UTF-8')
            msg.attach(html_msg)
        return msg
        
    header_start_re = re.compile(r'<header name="([^"]*)">')
    header_end_re = re.compile(r'</header>')
    def parse_headers(self, markup):
        """
        Looks for <header name="...">...</header> in an HTML file,
        and return (header_list, rest_of_body).

        header_list is a list of (name, content) tuples.
        """
        headers = []
        while 1:
            match_start = self.header_start_re.search(markup)
            if not match_start:
                break
            header_name = match_start.group(1)
            rest = markup[match_start.end():]
            match_end = self.header_end_re.search(rest)
            assert match_end, (
                "Bad markup, no </header> found: %r" % rest)
            content = rest[:match_end.start()]
            content = self.normalize_whitespace(content)
            headers.append((header_name.strip(), content))
            markup = (markup[:match_start.start()]
                      + markup[match_end.end()+match_start.end():])
        return headers, markup.strip()

    whitespace_re = re.compile(r'[ \t\n\r]+')
    def normalize_whitespace(self, s):
        s = s.strip()
        s = self.whitespace_re.sub(' ', s)
        return s

def popdefault(d, key, default=None):
    """
    Pop key from dictionary d (and return), or return default
    """
    if d.has_key(key):
        v = d[key]
        del d[key]
        return v
    else:
        return default
            
def send_mail(template, to_address, from_address,
              **options):
    """
    Send mail to to_address (a single email, or a list of emails),
    from from_address, using the given template.  If you give a
    string, it will be considered a filename and the template will be
    loaded from that location.

    All options (plus to_address and from_address) will be passed into
    the template as options.  Any options that start with 'header_'
    will also be used as headers (though the template can override
    these, and takes precedence).

    If you don't want to send HTML mail, use include_html=False;
    include_text=False to suppress the text version (though there's
    little purpose to doing that).

    The mail will be sent out via SMTP on the localhost.
    """
    
    if isinstance(template, str):
        # @@: it's a shame `here` is undefined for this case:
        template = EmailTemplate(template, None)
    msg = template(to_address=to_address, from_address=from_address,
                   **options)
    if isinstance(to_address, (str, unicode)):
        to_address = [to_address]
    for single_to_address in to_address:
        msg['To'] = single_to_address
    msg['From'] = from_address
    for name, value in options.items():
        if name.startswith('header_'):
            name = name[len('header_'):]
            if not msg.get(name):
                msg[name] = value
    smtp_server = options.get('smtp_server', 'localhost')
    server = smtplib.SMTP(smtp_server)
    server.sendmail(from_address, to_address, str(msg))
    server.quit()
    return msg
