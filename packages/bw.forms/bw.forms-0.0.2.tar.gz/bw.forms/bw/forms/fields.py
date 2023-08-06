from tw.forms import Form, ListMixin, FormField, SubmitButton
from tw.forms import ContainerMixin

__all__ = [
    'ListForm', 'InputField', 'TextField', 'FancySubmitButton',
    'ButtonLink', 'SubmitOrCancel',
    'PasswordField', 'InlineFieldList'
]

class InlineFieldList(ContainerMixin, FormField):
    template = 'bw.forms.templates.inline_field_list'

class ListForm(Form, ListMixin):
    engine = 'mako'
    template = 'bw.forms.templates.list_form'

class InputField(FormField):
    params = ['type']
    template = 'bw.forms.templates.input_field'

class TextField(InputField):
    params = ['size', 'maxlength']
    size__doc = 'The size of the text field'
    maxlength__doc = 'The max size of the field'
    type = 'text'

    def update_params(self, d):
        super(TextField, self).update_params(d)
        # leave out deprecation warning about max_size
        self.update_attrs(d, 'size', 'maxlength')

class PasswordField(InputField):
    type = 'password'

class FancySubmitButton(SubmitButton):
    params = ['img_src', 'submit_text']
    template = 'bw.forms.templates.fancy_submit_button'

class ButtonLink(FormField):
    params = ['href', 'img_src', 'submit_text']
    template = 'bw.forms.templates.button_link'
    suppress_label = True
    validator = None

class SubmitOrCancel(FormField):
    params = [
        'submit_text',
        'cancel_text',
        'submit_img_src',
        'cancel_img_src',
        'cancel_url',
        'submit_css_class',
        'cancel_css_class'
    ]

    template = 'bw.forms.templates.submit_or_cancel'
    suppress_label = True
    validator = None

    submit_css_class = 'button positive'
    cancel_css_class = 'button negative'

    submit_text = 'Submit'
    cancel_text = 'Cancel'
