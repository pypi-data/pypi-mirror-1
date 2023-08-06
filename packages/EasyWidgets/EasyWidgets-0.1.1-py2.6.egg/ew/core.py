from __future__ import with_statement
import logging
import string
from contextlib import contextmanager

import tg
from tg import expose
from pylons import c
from formencode import validators as fev
from formencode import schema as fes

try:
    from tg.decorators import variable_decode
except ImportError: # pragma no cover
    from tg.decorators import before_validate
    from formencode import variabledecode
    
    @before_validate
    def variable_decode(remainder, params):
        '''Best-effort formencode.variabledecode on the params before validation

        If any exceptions are raised due to invalid parameter names, they are
        silently ignored, hopefully to be caught by the actual validator.  Note that
        this decorator will *add* parameters to the method, not remove.  So for
        instnace a method will move from {'foo-1':'1', 'foo-2':'2'} to
        {'foo-1':'1', 'foo-2':'2', 'foo':['1', '2']}.
        '''
        try:
            new_params = variabledecode.variable_decode(params)
            params.update(new_params)
        except:
            pass

log = logging.getLogger(__name__)

class ExprTemplate(string.Template):
    idpattern = r'[_a-z][^}]*'

class Widget(fev.Validator):
    _id = 0
    # Params are copied to the template context from the widget
    params=[]
    perform_validation = False
    template=None

    class __metaclass__(fev.Validator.__metaclass__):
        '''Make sure that the params lists of base classes are additive'''
        def __new__(meta, name, bases, dct):
            params = []
            for b in bases:
                params += getattr(b, 'params', [])
            dct['params'] = params + dct.get('params', [])
            return type.__new__(meta, name, bases, dct)

    def __init__(self, **kw):
        params = kw.pop('params', [])
        self.params = self.__class__.params + params
        self._id = Widget._id
        Widget._id += 1
        for k,v in kw.iteritems():
            setattr(self, k, v)
        if self.template:
            expose(self.template)(self)

    def __call__(self, **kw):
        context = dict(
            (k, getattr(self, k))
            for k in self.params)
        context.update(kw)
        return context

    def validate(self, value, state):
        return self.to_python(value, state)

    def display(self, **kw):
        wi = WidgetInstance(self, dict(kw), parent=(getattr(c, 'widget', None) or None))
        return wi.display()

    def resources(self):
        return []

class ControllerWidget(Widget):
    def __init__(self, controller):
        self.controller = controller
        if controller.decoration.validation:
            self.validator = controller.decoration.validation.validators
        else:
            self.validator = None
        self.decoration = controller.decoration

    def __call__(self, **kw):
        response = self.controller(**kw)
        return response

    def to_python(self, value, state=None):
        s = self._make_schema()
        if s is None: return value
        return s.to_python(value, state)

    def from_python(self, value, state=None):
        try:
            s = self._make_schema()
            if s is None:
                return value
            if value is None:
                return None
            return s.from_python(value, state)
        except fev.Invalid, inv: # pragma no cover
            return value

    def _make_schema(self):
        if not isinstance(self.validator, dict):
            return self.validator
        kwargs = dict(self.validator)
        kwargs.update(allow_extra_fields=True,
                      filter_extra_fields=True)
        return fes.Schema(**kwargs)

class WidgetInstance(object):

    def __init__(self, widget_type, context=None, parent=None):
        if context is None: context = {}
        self.widget_type = widget_type
        self.context = context
        self.response = None
        self.parent = parent
        self.dc = tg.controllers.DecoratedController()

    def __repr__(self):
        return 'I-%r' % self.widget_type

    def display(self):
        if self.parent is None:
            # Initialize name, value, and errors
            if getattr(c, 'validation_exception', ''):
                self.context['errors'] = c.validation_exception.unpack_errors()
                self.context['value'] = c.validation_exception.value
            else:
                self.context['value'] = self.widget_type.from_python(self.context.get('value'), None)
            if getattr(self.widget_type, 'name', None):
                try:
                    # Special handling for named forms
                    self.context['value'] = self.context.get('value', {}).get(
                        self.widget_type.name)
                except AttributeError:
                    log.warning('Apparently someone sent a named widget that was'
                                ' not enclosed in a form (the value param was not'
                                ' a dict)')
                self.context['name'] = self.widget_type.name
                    
        response = self.widget_type(**self.context)
        if self.parent:
            # Underlay parent response fields
            d = dict(self.parent.response)
            d.update(response)
            response = d
        self.response = response
        
        with _push_context(c, widget=self):
            try:
                response = self.dc._render_response(self.widget_type, response)
            except Exception, ex:
                log.exception('Error rendering %s', self.widget_type)
                raise
        return response

    def subwidget(self, id, context):
        return self.widget_type.subwidget(self, id, context)

    def expand(self, tpl):
        '''Peform basic string.Template expansion in the current context'''
        tpl = ExprTemplate(unicode(tpl))
        context = ExprDict(self.response or self.context)
        return tpl.safe_substitute(context)

    def context_for(self, id=None):
        '''Return the context for the identified subwidget.  At a
        minimum, this will always return a dict with name, value, and errors
        present.
        '''
        if isinstance(id, basestring):
            result = self._context_for_str(id)
        elif isinstance(id, int):
            result = self._context_for_int(id)
        else:
            result = dict(self.context)
        result.setdefault('name', None)
        result.setdefault('value', None)
        result.setdefault('errors', None)
        return result

    def _context_for_str(self, name):
        result = dict(self.context)
        if self.context.get('name'):
            result['name'] = self.context['name'] + '.' + name
        else:
            result['name'] = name
        result['value'] = _safe_getitem(result, 'value', name)
        result['errors'] = _safe_getitem(result, 'errors', name)
        return result

    def _context_for_int(self, index):
        result = dict(self.context)
        if self.context['name']:
            result['name'] = '%s-%d' % (self.context['name'], index)
        result['value'] = _safe_getitem(result, 'value', index)
        result['errors'] = _safe_getitem(result, 'errors', index)
        return result

class WidgetsList(list):
    '''Simple class to let you create a list of widgets declaratively'''
    class __metaclass__(type):
        def __new__(meta, name, bases, dct):
            if bases == (list,):
                return type.__new__(meta, name, bases, dct)
            result = []
            for k,v in dct.iteritems():
                if isinstance(v, Widget):
                    if v.name is None:
                        v.name = k
                    if getattr(v, 'label', None) is None:
                        v.label = k.replace('_', ' ').title()
                    result.append(v)
            # Maintain declaration order
            result.sort(key=lambda w:w._id)
            return result

def _safe_getitem(dct, key, item):
    '''Return either dct[key][item],  dct[key].item, or None, whichever
    is appropriate
    '''
    if key not in dct: return None
    value = dct[key]
    try:
        result = value[item]
    except TypeError:
        if isinstance(item, str):
            result = getattr(value, item, None)
        else:
            result = None
    except (KeyError, IndexError), ex:
        result = None
    return result

@contextmanager
def _push_context(obj, **kw):
    '''Temporarily add attributes to 'obj', restoring 'obj' to its original
    state on __exit__
    '''
    new_keys = [ k for k in kw if not hasattr(obj, k) ]
    saved_items = [
        (k, getattr(obj, k)) for k in kw
        if hasattr(obj, k) ]
    for k,v in kw.iteritems():
        setattr(obj, k, v)
    yield obj
    for nk in new_keys:
        delattr(obj, nk)
    for k,v in saved_items:
        setattr(obj, k, v)

class ExprDict(dict):

    def get(self, k, *args):
        try:
            return self[k]
        except KeyError:
            if args: return args[0]
            raise

    def __getitem__(self, k):
        try:
            return eval(k, dict(self))
        except KeyError, ke:
            raise
        except Exception, ex:
            return '[Exception in %s: %s]' % (k, ex)
            
            
