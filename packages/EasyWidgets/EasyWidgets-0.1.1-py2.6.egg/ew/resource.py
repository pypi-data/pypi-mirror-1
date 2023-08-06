from __future__ import with_statement
import logging
import os.path
from itertools import chain
from mimetypes import guess_type
from collections import defaultdict

import pkg_resources
from pylons import c, request
from tg import expose, response, controllers
from webob import exc

from .core import Widget, ControllerWidget, WidgetInstance

log = logging.getLogger(__name__)

class ResourceManager(object):
    location = [ 'head_css', 'head_js',
                 'body_top_js', 'body_js' ]
    block_size = 4096
    paths = []

    @classmethod
    def get(cls):
        if not getattr(c, '_ew_resources', None):
            c._ew_resources = cls()
        return c._ew_resources

    @classmethod
    def register_directory(cls, url_path, directory):
        for up,dir in cls.paths:
            if up == url_path: return
        cls.paths.append((url_path, directory))

    @classmethod
    def register_all_resources(cls):
        for ep in pkg_resources.iter_entry_points('easy_widgets.resources'):
            log.info('Loading ep %s', ep)
            ep.load()(cls)

    def __init__(self, script_name='/_ew_resources/'):
        self.resources = defaultdict(list)
        self.script_name = script_name

    def emit(self, location):
        seen_resources = set()
        for resource in self.resources[location]:
            if resource.squash and resource in seen_resources: continue
            seen_resources.add(resource)
            yield resource.display()
            yield '\n'

    def register_widgets(self, context):
        for name in dir(context):
            w = getattr(context, name)
            if isinstance(w, (Widget, WidgetInstance, Resource)):
                log.debug('Registering resources for %s', w)
                self.register(w)

    def register(self, resource):
        if isinstance(resource, Resource):
            assert resource.location in self.location, \
                'Resource.location must be one of %r' % self.location
            self.resources[resource.location].append(resource)
            resource.manager = self
        elif isinstance(resource, Widget):
            for r in resource.resources(): self.register(r)
        elif isinstance(resource, WidgetInstance):
            for r in resource.widget_type.resources(): self.register(r)
        else:
            raise AssertionError, 'Unknown resource type %r' % resource

    @expose(content_type=controllers.CUSTOM_CONTENT_TYPE)
    def _default(self, *args, **kwargs):
        res_path = request.path_info[len(self.script_name):]
        fs_path = self.get_filename(res_path)
        if fs_path is None:
            log.warning('Could not map %s', res_path)
            log.info('Mapped directories: %r', self.paths)
            raise exc.HTTPNotFound(res_path)
        file_iter = self._serve_file(fs_path, res_path)
        # Make sure 404s are raised appropriately
        return chain([ file_iter.next() ], file_iter)
    default=_default

    def get_filename(self, res_path):
        for url_path, directory in self.paths:
            if res_path.startswith(url_path):
                fs_path = os.path.join(
                    directory,
                    res_path[len(url_path)+1:])
                if not fs_path.startswith(directory):
                    return None
                return fs_path
        return None
    
    def _serve_file(self, fs_path, res_path):
        try:
            response.headers['Content-Type'] = ''
            content_type = guess_type(fs_path)
            if content_type: content_type = content_type[0]
            else: content_type = 'application/octet-stream'
            response.content_type = content_type
        except TypeError:
            log.error('Error in _Serve_file')
        try:
            with open(fs_path, 'rb') as fp:
                while True:
                    buffer = fp.read(self.block_size)
                    if not buffer: break
                    yield buffer
        except IOError:
            log.warning('Could not find %s', res_path)
            raise exc.HTTPNotFound(res_path)

    def __repr__(self):
        l = ['<ResourceManager>']
        for name, res in self.resources.iteritems():
            l.append('  <Location %s>' % name)
            for r in res: l.append('    %r' % r)
        for u,d in self.paths:
            l.append('  <Path url="%s" directory="%s">' % (u, d))
        return '\n'.join(l)

class ResourceHolder(Widget):

    def __init__(self, *resources):
        self._resources = resources

    def resources(self):
        return self._resources

class Resource(object):

    def __init__(self, location, widget, context, squash=True):
        self.location = location
        self.widget = widget
        self.context = context
        self.squash = squash
        self.manager = None

    def display(self):
        wi = WidgetInstance(self.widget, self.context)
        return wi.display()

class ResourceLink(Resource):

    def __init__(self, url, location, squash):
        self._url = url
        super(ResourceLink, self).__init__(
            location, ControllerWidget(self.index), {}, squash)

    def url(self):
        if '//' not in self._url and not self._url.startswith('/'):
            return self.manager.script_name + self._url
        return self._url

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self._url)

    def __hash__(self):
        return hash(self.location) + hash(self._url) + hash(self.squash)

    def __eq__(self, o):
        return (self.__class__ == o.__class__
                and self._url == o._url
                and self.location == o.location
                and self.squash == o.squash)

class JSLink(ResourceLink):

    def __init__(self, url, location='body_js', squash=True):
        super(JSLink, self).__init__(url, location, squash)

    @expose('genshi:ew.templates.jslink')
    def index(self, **kwargs):
        return dict(href=self.url())

class CSSLink(ResourceLink):

    def __init__(self, url, **attrs):
        self.attrs = attrs
        super(CSSLink, self).__init__(url, 'head_css', True)

    @expose('genshi:ew.templates.csslink')
    def index(self, **kwargs):
        return dict(href=self.url(), attrs=self.attrs)

class ResourceScript(Resource):

    def __init__(self, text, location, squash):
        self.text = text
        super(ResourceScript, self).__init__(
            location, ControllerWidget(self.index), {}, squash)

    def __hash__(self):
        return hash(self.text) + hash(self.location) + hash(self.squash)

    def __eq__(self, o):
        return (self.__class__ == o.__class__
                and self.text == o.text
                and self.location == o.location
                and self.squash == o.squash)

class JSScript(ResourceScript):

    def __init__(self, text, location='body_js', squash=True):
        super(JSScript, self).__init__(text, location, squash)

    @expose('genshi:ew.templates.jsscript')
    def index(self, **kwargs):
        return dict(text=self.text)

class CSSScript(Resource):

    def __init__(self, text):
        super(CSSScript, self).__init__(text, 'head_css', True)

    @expose('genshi:ew.templates.csscript')
    def index(self, **kwargs):
        return dict(text=self.text)

class GoogleAnalytics(Resource):

    def __init__(self, account):
        self.account = account
        super(GoogleAnalytics, self).__init__(
            'head_js', ControllerWidget(self.index), {}, True)

    @expose('genshi:ew.templates.google_analytics')
    def index(self, **kwargs):
        return dict(account=self.account)
