try:
    import paste.wareweb.event as event
except ImportError:
    import wareweb.event as event
    
import sys
import os
import templatetools
import emailtemplate

class ZPTComponent(object):

    def __init__(self):
        self.template_pool = templatetools.TemplatePool(
            templatetools.FilePageTemplate)
        self.email_template_pool = templatetools.TemplatePool(
            emailtemplate.EmailTemplate)

    def __addtoclass__(self, attr, cls):
        cls.listeners.append(self.servlet_event)
        self.name = attr

    def servlet_event(self, name, servlet, *args, **kw):
        if name == 'start_awake':
            return self.awake_event(servlet, *args, **kw)
        if name == 'start_sleep':
            return self.sleep_event(servlet, *args, **kw)
        if name == 'start_respond':
            return self.respond_event(servlet, *args, **kw)
        return event.Continue
            
    def awake_event(self, servlet, next_method, call_setup=None):
        servlet._zpt_used_templates = []
        servlet.context = AttrDict(servlet=servlet,
                                   request=servlet.fields)
        servlet.options = AttrDict()
        servlet._zpt_setup_done = 1
        servlet.view = '<DEFAULT>'
        setattr(servlet, self.name, MethodProxy(servlet, self))
        return event.Continue

    def sleep_event(self, servlet, next_method):
        if getattr(servlet, '_zpt_setup_done', None):
            for template, pool in servlet._zpt_used_templates:
                pool.returnTemplate(template)
            del servlet._zpt_used_templates
            del servlet.context
            del servlet.options
        return event.Continue

    def respond_event(self, servlet, next_method):
        if servlet.view is None:
            return event.Continue
        self.write_template(servlet)
        return None

    def template_paths(self, servlet):
        config = servlet.config
        base_dirs = config.get('template_paths', [])
        if not base_dirs:
            base_dirs = ['templates/']
        return [
            os.path.join(config['root_path'], dir)
            for dir in base_dirs]

    _tmpl_pools = {}
    _email_pools = {}

    def get_pool(self, here_dirs, pool, *args):
        key = (here_dirs, args)
        try:
            return pool[key]
        except KeyError:
            pool[key] = templatetools.TemplatePool(
                here_dirs, *args)
            return pool[key]

    def smtp_server(self, servlet):
        return servlet.config.get('smtp_server', 'localhost')

    def write_template(self, servlet):
        view = servlet.view
        if view is None:
            return
        if view == '<DEFAULT>':
            module_path = os.path.abspath(sys.modules[servlet.__class__.__module__].__file__)
            base_path = servlet.config['publish_dir']
            assert module_path.startswith(base_path), (
                "Module path (%r) is not under publish_dir path (%r)"
                % (module_path, base_path))
            servlet_path = os.path.splitext(module_path[len(base_path)+1:])[0]
            assert not servlet_path.startswith('/'), (
                "Servlet path should not start with /: %r" % servlet_path)
            template_path = servlet_path
        else:
            template_path = view
        if not template_path.endswith('.pt'):
            template_path += '.pt'
        template = self.template(servlet, template_path)
        servlet.write(
            template(context=servlet.context, **servlet.options))

    def template(self, servlet, base_filename, pool=None):
        """
        Fetches the named template.  Performs some checks, and keeps
        track of the template so it can be returned to the pool.
        """
        if pool is None:
            pool = self.get_pool(tuple(self.template_paths(servlet)),
                                 self._tmpl_pools,
                                 templatetools.FilePageTemplate)
        template = pool.get_template(base_filename)
        return template

    def send_mail(self, servlet, filename, to_address, from_address,
                  **options):
        pool = self.get_pool(tuple(self.template_paths(servlet)),
                             self._email_pool,
                             emailtemplate.EmailTemplate)
        template = self.template(servlet, filename, pool=pool)
        if not options.has_key('smtp_server'):
            options['smtp_server'] = self.smtp_server(servlet)
        return emailtemplate.send_mail(template, to_address=to_address,
				       from_address=from_address,
				       **options)
        
class MethodProxy(object):

    def __init__(self, servlet, zpt):
        self.servlet = servlet
        self.zpt = zpt

    def write_template(self, *args, **kw):
        return self.zpt.write_template(self.servlet, *args, **kw)

    def template(self, *args, **kw):
        return self.zpt.template(self.servlet, *args, **kw)

    def send_mail(self, *args, **kw):
        return self.zpt.send_mail(self.servlet, *args, **kw)

class AttrDict(dict):

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError
        return self[attr]

    def __setattr__(self, attr, value):
        if attr.startswith('_'):
            raise AttributeError
        self[attr] = value
