from pylons.i18n import ugettext as _, lazy_ugettext as l_

from .fields import CompoundField, SubmitButton

class SimpleForm(CompoundField):
    template = 'ew.templates.simple_form'
    params = [ 'method', 'action', 'submit_text', 'buttons', 'enctype' ]
    method='POST'
    action=None
    submit_text='Submit'
    enctype=None
    show_label=False
    buttons=None
    button_class = SubmitButton

    def __init__(self, **kw):
        buttons = kw.get('buttons', self.buttons)
        submit_text = kw.get('submit_text', self.submit_text)
        extra_fields = kw.get('extra_fields', list(self.extra_fields))
        if extra_fields is None:
            extra_fields = kw['extra_fields'] = []
        if buttons is None:
            buttons=kw['buttons'] = []
        else:
            buttons = kw['buttons'] = list(buttons)
        if submit_text is not None:
            buttons.insert(0, self.button_class(label=l_(submit_text)))
        kw['extra_fields'] = extra_fields + buttons
        super(SimpleForm, self).__init__(**kw)

    def to_python(self, value, state):
        if self.name: value = value.get(self.name)
        result = super(SimpleForm, self).to_python(value, state)
        if self.name: result = dict({self.name:result})
        return result

    def from_python(self, value, state):
        if self.name: value = value.get(self.name)
        result = super(SimpleForm, self).from_python(value, state)
        if self.name: result = dict({self.name:result})
        return result

