from django.template import Library, Node
from django import forms
import re

register = Library()

SPLIT_RE = re.compile(r'[\s,]+')

def show_form(form, wrap_with_tag='div'):
    "Render all fields in `form`, passing `wrap_with_tag` to `show_field`."
    return {'form': form, 'tag': wrap_with_tag}
register.inclusion_tag("forms/form.html")(show_form)

def show_field(field, wrap_with_tag='div', classes=()):
    "Render `field` (label, input, and help text) encosed in `wrap_with_tag`."
    if isinstance(classes, basestring):
        classes = classes.split(',')
    is_checkbox = (
        isinstance(field.field.widget, forms.widgets.CheckboxInput) or
        getattr(field.field.widget, 'input_type', None) == 'checkbox'
    )
    is_radio = (
        isinstance(field.field.widget, forms.widgets.RadioInput) or
        getattr(field.field.widget, 'input_type', None) == 'radio'
    )
    return {
        'field': field,
        'errors': field.errors,
        'is_hidden': field.is_hidden,
        'is_checkbox': is_checkbox,
        'is_radio': is_radio,
        'tag': wrap_with_tag,
        'classes': classes,
        'required': field.field.required
    }
register.inclusion_tag("forms/field.html")(show_field)

def show_errors(field_or_errors, errors=None):
    if errors is None:
        if isinstance(field_or_errors, forms.forms.BoundField):
            field = field_or_errors
            errors = field.errors
        else:
            field = None
            errors = field_or_errors
    else:
        field = field_or_errors
    return {'field': field, 'errors': errors}
register.inclusion_tag("forms/errors.html")(show_errors)

def show_label(field, label=None, classes=()):
    "Render the label tag for `field`, overriding its label text with `label`."
    if label is None:
        label = field.label
    if isinstance(classes, basestring):
        classes = SPLIT_RE.split(classes)
    return {
        'field': field,
        'label': label,
        'classes': classes,
        'required': field.field.required
    }
register.inclusion_tag("forms/label.html")(show_label)

def show_help_text(field_or_text, classes=()):
    "Render the text or the field's help text given by `field_or_text`."
    if isinstance(field_or_text, basestring):
        field = None
        help_text = field_or_text
    else:
        field = field_or_text
        help_text = field.help_text
    if isinstance(classes, basestring):
        classes = SPLIT_RE.split(classes)
    return {'field': field, 'help_text': help_text, 'classes': classes}
register.inclusion_tag("forms/help_text.html")(show_help_text)

def do_class_list(parser, token):
    "Resolve arguments, flatten lists, and split strings to get class names."
    bits = token.split_contents()[1:]
    class_vars = [parser.compile_filter(bit) for bit in bits]
    return ClassListNode(class_vars)
register.tag('class_list', do_class_list)

def do_class_attr(parser, token):
    """
    Render a HTML class attribute if the given classes are non-empty,
    otherwise returns an empty string to avoid including an empty attribute.
    Takes the same arguments as `class_list`. The attribute name is prefixed
    with a space to help avoid extraneous spaces.
    
    """
    bits = token.split_contents()[1:]
    class_vars = [parser.compile_filter(bit) for bit in bits]
    return ClassListNode(class_vars, ' class="%s"')
register.tag('class_attr', do_class_attr)

class ClassListNode(Node):
    def __init__(self, class_vars, output_format="%s"):
        self.class_vars = class_vars
        self.output_format = output_format
    
    def render(self, context):
        classes = [var.resolve(context) for var in self.class_vars]
        class_names = []
        for class_ in classes:
            if isinstance(class_, basestring):
                class_ = [class_]
            for names in class_:
                for name in SPLIT_RE.split(names):
                    if name and name not in class_names:
                        class_names.append(name)
        value = " ".join(class_names)
        return value and self.output_format % value
