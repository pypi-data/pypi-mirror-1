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
templatetools.py

Tools for using ZopePageTemplates, primarily intended for use with
Webware.

Typically you will use TemplatePool, storing an instance of the pool.
To get a template, use aPool.get_template(filename) -- this reuse a
template if possible.

The other interesting tool is ContextWrapper.  This is a thin wrapper
that give you access to the template's namespace.  Any object can
define the method ``__render_with_namespace__`` and if the object is
rendered in a template then that method will be called with a single
argument -- a dictionary-like object containing the namespace.  But
this is awkward when you have a method (rather than a full blown
object) that you want to render using the namespace.  ContextWrapper
takes a function argument, and when it is rendered, it in turn calls
that function with the namespace argument.  A small example is in that
class.
"""

__all__ = ['FilePageTemplate', 'TemplatePool', 'ContextWrapper']

import os
try:
    from ZopePageTemplates import PageTemplate
    from ZopePageTemplates import PTRuntimeError
except ImportError:
    # @@: really, you only get the ZopePageTemplates package when
    # you install into a non-system directory, where .pth files
    # are ignored
    import PageTemplate
    import PTRuntimeError
import types
pkg_resources = None

class TemplatePool(object):

    def __init__(self, here_dirs, pt_class=None):
        self.here_dirs = here_dirs
        self.pt_class = pt_class or FilePageTemplate
        self.here = HereSpace(self.get_template_or_dir)
        self.templates = {}
        self.egg = EggSpace(self.make_template)

    def add_template_path(self, path, position=None):
        if path in self.here_dirs:
            return
        here_dirs = list(self.here_dirs)
        if position is None:
            here_dirs.append(path)
        else:
            here_dirs.insert(position, path)
        self.here_dirs = tuple(here_dirs)

    def get_template(self, filename, refresh=True, dir=None):
        filename = filename.lstrip(os.sep)
        if filename.startswith('here/'):
            filename = filename[5:].lstrip(os.sep)
        if filename.startswith('egg/'):
            filename = filename[4:].lstrip(os.sep)
            ob = self.egg
            for path_part in filename.split('/'):
                ob = ob[path_part]
            return ob
        if dir is None:
            for pt_dir in self.here_dirs:
                if os.path.exists(os.path.join(pt_dir, filename)):
                    dir = pt_dir
                    break
            else:
                raise KeyError(
                    "No template %s found (looked in %s)"
                    % (filename, ', '.join(self.here_dirs)))
        if filename in self.templates:
            tmpl = self.templates[(dir, filename)]
        else:
            tmpl = self.templates[(dir, filename)] = self.make_template(dir, filename)
        if refresh:
            # @@: This can't detect that a new file has been added to
            # another directory listed in here_dirs that would shadow
            # this template
            tmpl.refresh()
        return tmpl

    def get_template_or_dir(self, filename, dirs=None):
        if dirs is None:
            dirs = self.here_dirs
        filename = filename.lstrip(os.sep)
        for pt_dir in dirs:
            if os.path.exists(os.path.join(pt_dir, filename)):
                if os.path.isdir(os.path.join(pt_dir, filename)):
                    return HereSpace(
                        self.get_template_or_dir,
                        ([os.path.join(pt_dir, filename)],))
                else:
                    return self.get_template(filename, dir=pt_dir)
        else:
            raise KeyError(
                "No template or dir %s found (looked in %s)"
                % (filename, ', '.join(dirs)))

    def make_template(self, filename, *args):
        if args:
            filename = os.path.join(filename, *args)
        tmpl = self.pt_class(filename, self.here, egg=self.egg)
        if tmpl._v_errors:
            raise PTRuntimeError(
                'Template %s has errors:\n%s\n%s'
                % (filename, tmpl._v_errors[0], tmpl._v_errors[1]))
        return tmpl

    def __repr__(self):
        return ('<TemplatePool %s here_dirs=%s pt_class=%s>'
                % (hex(abs(id(self)))[2:], self.here_dirs,
                   self.pt_class))

class HereSpace(object):

    """
    This implements 'here' for page templates, where 'here' is a space
    that supports fetching other templates.  I.e., when you do::

        <metal:tpl use-macro="here/standard_template.pt/macros/page">

    this is the 'here' that finds 'standard_template.pt'.

    You must also provide it with a subclass of PageTemplate that can
    accept a filename as its only constructor argument.  (Or
    potentially it can be some other factory function that creates
    PageTemplate instances)
    """

    def __init__(self, factory, factory_args=()):
        self.factory = factory
        self.factory_args = factory_args

    def __getitem__(self, key):
        assert '/' not in key, "Keys cannot have '/'s: %r" % key
        return self.factory(key, *self.factory_args)

    def __repr__(self):
        return ('<%s %s, factory=%s %s>'
                % (self.__class__.__name__,
                   hex(abs(id(self)))[2:], self.factory,
                   self.factory_args))


class FilePageTemplate(PageTemplate):

    """
    This is a page template that is based on a file.  Each template is
    passed a filename argument, and the template is read from that
    file.  The template may be reread (if it has changed) anytime you
    call .refresh().  You may wish to do this at the beginning of a
    request.

    It adds 'here' to the context, which is a namespace for the
    directory in which it is contained (using FileNamespace).
    Specifically this makes this work::

        <html metal:use-macro="here/standard_template.pt/macros/page">

    You can pass in here_dir if you want to use a separate directory.
    Sometimes this will be a fixed directory, since there is currently
    no way to traverse from 'here' to a parent directory.
    """

    def __init__(self, filename, here, **other_vars):
        self.filename = filename
        self.mtime = 0
        self.refresh()
        self.here = here
        self.other_vars = other_vars
        
    def refresh(self):
        mtime = os.stat(self.filename).st_mtime
        if mtime > self.mtime:
            self.mtime = mtime
            self.read_file(self.filename)

    def read_file(self, filename):
        f = open(self.filename, 'rb')
        self.write(f.read())
        f.close()

    def __call__(self, context=None, *args, **kw):
        if context is None:
            context = {}
        if not kw.has_key('args'):
            kw['args'] = args
        elif args:
            assert 0, "You cannot both pass in a keyword argument 'args', and positional arguments"
        extra_context = {'options': kw, 'here': self.here,
                         'test': test}
        extra_context.update(self.other_vars)
        context.update(extra_context)
        return self.pt_render(extra_context=context)

    def __repr__(self):
        return ('<%s %s %s>'
                % (self.__class__.__name__, hex(abs(id(self)))[2:], self.filename))


class EggSpace(object):

    """
    This loads templates from an egg or entry point.  Use like::

        <metal:tpl use-macro="egg/EggName/entry_name/template_name.pt">

    Or simply:

        <metal:tpl use-macro="egg/EggName/template_name.pt">

    will use the entry point named 'main'.
    """

    def __init__(self, factory):
        self.factory = factory

    def __getitem__(self, key):
        global pkg_resources, _resource_manager
        if pkg_resources is None:
            import pkg_resources
            _resource_manager = pkg_resources.ResourceManager()
        egg = pkg_resources.get_distribution(key)
        return EggTemplateSpace(egg, key, self.factory)

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

class EggTemplateSpace(object):

    def __init__(self, egg, spec, factory):
        self.egg = egg
        self.spec = spec
        self.egg_map = self.egg.get_entry_map(
            'zptkit.template_dir')
        if not self.egg_map:
            raise KeyError(
                "The Egg %s (from %s) has no zptkit.template_dir entry points"
                % (self.egg, self.egg.location))
        self.factory = factory

    def __getitem__(self, key):
        # First see if it's an entry point:
        if key in self.egg_map:
            return EggEntryPoint(self.factory,
                                 self.egg,
                                 key,
                                 self.egg_map[key].load())
        elif 'main' in self.egg_map:
            return EggEntryPoint(self.factory,
                                 self.egg,
                                 'main',
                                 self.egg_map['main'].load())[key]
        else:
            raise KeyError(
                "The Egg %s doesn't have an entry point %r or a main "
                "entry point" % (self.egg, key))

    def __repr__(self):
        return '<%s for %s>' % (self.__class__.__name__, self.egg)

class EggEntryPoint(object):

    def __init__(self, factory, egg, entry_point_name,
                 resource_name):
        self.factory = factory
        self.egg = egg
        self.entry_point_name = entry_point_name
        self.resource_name = resource_name

    def __getitem__(self, key):
        new = self.resource_name + '/' + key
        if not self.egg.has_resource(new):
            raise KeyError(
                "Resource %s in %s#%s does not exist"
                % (new, self.egg, self.entry_point_name))
        if self.egg.resource_isdir(new):
            return self.__class__(
                self.factory, self.egg, self.entry_point_name, new)
        fn = self.egg.get_resource_filename(_resource_manager, new)
        return self.factory(fn)

    def __repr__(self):
        return '<%s for %s#%s (%s)>' % (
            self.__class__.__name__, self.egg, self.entry_point_name,
            self.resource_name)

class ContextWrapper:

    """
    This is used when you don't want to create a new object just to
    render a small bit of content in a way that is aware of the
    PageTemplate context.  You use it like::

        class MyClass:
            def getLink(self, ns):
                do stuff with ns...
            link = ContextWrapper(getLink)

    Then when someone does <span tal:replace="aMyClass/link"> they
    will be calling the getLink function.
    """

    def __init__(self, callback, *args, **kw):
        self.callback = callback
        self.args = args
        self.kw = kw

    def __render_with_namespace__(self, ns):
        return self.callback(ns, *self.args, **self.kw)

def test(conditional, true_value, false_value=None):
    """
    A standard function in the context, like a trinary if/then/else
    operator, except that true_value and false_value are always
    evaluated.  A safer alternative to ``cond and true_value or
    false_value``
    """
    if conditional:
        return true_value
    else:
        return false_value

