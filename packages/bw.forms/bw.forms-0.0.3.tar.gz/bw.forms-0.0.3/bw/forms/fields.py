from tw.forms import Form, ListMixin, FormField, SubmitButton
from tw.forms import ContainerMixin

from tw.forms import ListForm, InputField, TextField, PasswordField

ListForm.engine = 'mako'
ListForm.template = 'bw.forms.templates.list_form'

InputField.template = 'bw.forms.templates.input_field'

class InlineFieldList(ContainerMixin, FormField):
    template = 'bw.forms.templates.inline_field_list'

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
