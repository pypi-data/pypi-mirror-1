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
"""
A component to use ZPT for rendering the body of a page.

You can handle templates on your own using this, by calling
self.template(filename) to get a template.  The templates are
automatically pooled and refreshed from disk in this mode.

You can also use the view mechanism, using
self.setView('template_name').  Then you should override your
servlet's writeHTML method, to look like::

    def writeHTML(self):
        self.writeTemplate()

The default template/view will match the servlet's name, e.g., the
Main servlet uses the Main.pt template.

You must pass in the path to the templates to the component
constructor, like::

    components = [ZPTComponent('/path/to/templates')]

If you give a relative path for this setting, it will be relative
to the directory *above* the directory containing the servlet.
"""

import sys
import os
import cgi
from Component.component import Component, ServletComponent
import templatetools
import emailtemplate
import ExceptionFormatter
from shadowdict import ShadowDict

class ZPTServletComponent(ServletComponent):

    _servletMethods = ['writeTemplate', 'context', 'options',
                       'template', 'sendMail',
                       'renderTemplate', 'add_template_path']

    def __init__(self, template_paths,
		 smtp_server='localhost',
                 use_exception_formatter=True,
                 default_encoding='UTF-8'):
        if isinstance(template_paths, (str, unicode)):
            template_paths = [template_paths]
        template_paths = tuple(template_paths)
        self.template_paths = template_paths
	self.smtp_server = smtp_server
        self.context = ShadowDict(self, '_context')
        self.options = ShadowDict(self, '_options')
        self.template_pool = self.get_pool(
            template_paths, self._tmpl_pools,
            templatetools.FilePageTemplate)
        self.email_pool = self.get_pool(
            template_paths, self._email_pools,
            emailtemplate.EmailTemplate)
        self.use_exception_formatter = use_exception_formatter
        self.default_encoding = default_encoding

    _tmpl_pools = {}
    _email_pools = {}

    def add_template_path(self, path, position=None):
        """
        Add a path to look for templates in.  `position` gives the
        position in the search order (0 for highest, None for last).
        """
        tmpl_paths = list(self.template_paths)
        if path in tmpl_paths:
            return
        if position is None:
            tmpl_paths.append(path)
        else:
            tmpl_paths.insert(position, path)
        self.template_paths = tuple(tmpl_paths)
        self.template_pool.add_template_path(path, position)
        self.email_pool.add_template_path(path, position)

    def get_pool(self, here_dirs, pool, *args):
        key = (here_dirs, args)
        try:
            return pool[key]
        except KeyError:
            pool[key] = templatetools.TemplatePool(here_dirs, *args)
            return pool[key]

    def awakeEvent(self, trans):
        self._used_templates = []
        self._context = {'servlet': self.servlet(),
                         'request': trans.request().fields()}
        self._options = {}
        self._setupDone = 1
        env = trans.request().environ()
        if env.get('paste.config', {}).get('zpt_debug'):
            self._debugging = True
        else:
            self._debugging = False
        return True

    def sleepEvent(self, trans):
        if getattr(self, '_setupDone', None):
            for template, pool in self._used_templates:
                pool.returnTemplate(template)
            del self._used_templates
            del self._context
            del self._options
            self._setupDone = 0
        return True

    def writeTemplate(self):
        view = self.servlet().view()
        if view is None:
            return
        if view == 'writeContent':
            module_path = os.path.abspath(sys.modules[self.servlet().__class__.__module__].__file__)
            context_path = self.servlet().request().serverSideContextPath()
            if 'zptkit.base_package' in self.servlet().request().environ():
                mod_name = self.servlet().request().environ()['zptkit.base_package']
                mod = sys.modules[mod_name]
                context_path = os.path.dirname(mod.__file__)
            assert module_path.startswith(context_path), (
                "Module path (%r) is not under Context path (%r)"
                % (module_path, context_path))
            servlet_path = os.path.splitext(module_path[len(context_path)+1:])[0]
            assert not servlet_path.startswith('/'), (
                "Servlet path should not start with /: %r" % servlet_path)
            template_path = servlet_path
        else:
            template_path = view
        if not template_path.endswith('.pt'):
            template_path += '.pt'
        template = self.template(template_path)
        text = self.renderTemplate(template)
        write = self.servlet().response().write
        write(text)
        if self._debugging:
            write('<br><table style="font-size: small">')
            items = self._options.items()
            items.sort()
            for name, value in items:
                value = repr(value)
                if len(value) > 70:
                    value = value[:65] + '...' + value[-5:]
                write('<tr><td style="text-align: right; padding-right: 1em">%s</td><td style="border-top: 1px solid #ddd">%s</td></tr>'
                      % (cgi.escape(name), cgi.escape(value)))
            write('</table>')

    def renderTemplate(self, template):
        if isinstance(template, (str, unicode)):
            template = self.template(template)
        try:
            text = template(context=self._context, **self._options)
            if isinstance(text, unicode):
                text = text.encode(self.default_encoding)
            return text
        except:
            # @@: this should fit into Webware's exception formatting
            # better.
            if not self.use_exception_formatter:
                raise
            # Detect Paste, which handles ZPT-style exceptions natively:
            if 'paste.config' in self.servlet().request().environ():
                raise
            t, v, tb = sys.exc_info()
            result = ExceptionFormatter.format_exception(
                t, v, tb, as_html=True)
            header = result[0]
            result = result[1:]
            return '\n'.join(result)

    def template(self, base_filename, pool=None):
        """
        Fetches the named template.
        """
        if pool is None:
            pool = self.template_pool
        return pool.get_template(base_filename)

    def sendMail(self, filename, to_address, from_address,
		 **options):
        template = self.template(filename, pool=self.email_pool)
        if 'smtp_server' not in options:
            options['smtp_server'] = self.smtp_server
        return emailtemplate.send_mail(template, to_address=to_address,
				       from_address=from_address,
				       **options)
        
class ZPTComponent(Component):

    _componentClass = ZPTServletComponent
