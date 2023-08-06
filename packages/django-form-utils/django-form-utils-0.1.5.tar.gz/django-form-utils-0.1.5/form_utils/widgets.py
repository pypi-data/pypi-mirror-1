"""
widgets for django-form-utils

Time-stamp: <2009-09-02 23:14:21 carljm widgets.py>

parts of this code taken from http://www.djangosnippets.org/snippets/934/
 - thanks baumer1122

"""
import os

from PIL import Image

from django import forms
from django.conf import settings
from django.utils.functional import curry
from django.utils.safestring import mark_safe
from django.core.files.uploadedfile import SimpleUploadedFile as UploadedFile

try:
    from sorl.thumbnail.main import DjangoThumbnail
    def thumbnail(image_path):
        t = DjangoThumbnail(relative_source=image_path, requested_size=(200,200))
        return u'<img src="%s" alt="%s" />' % (t.absolute_url, image_path)
except ImportError:
    def thumbnail(image_path):
        absolute_url = os.path.join(settings.MEDIA_ROOT, image_path)
        return u'<img src="%s" alt="%s" />' % (absolute_url, image_path)

class ImageWidget(forms.FileInput):
    template = '%(input)s<br />%(image)s'

    def __init__(self, attrs=None, template=None):
        if template is not None:
            self.template = template
        super(ImageWidget, self).__init__(attrs)
    
    def render(self, name, value, attrs=None):
        input_html = super(forms.FileInput, self).render(name, value, attrs)
        file_name = str(value)
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        try: # is image
            Image.open(file_path)
            image_html = thumbnail(str(value))
            output = self.template % {'input': input_html,
                                      'image': image_html}
        except IOError: # not image
            output = input_html
        return mark_safe(output)

class ClearableFileInput(forms.MultiWidget):
    default_file_widget_class = forms.FileInput
    template = '%(input)s Clear: %(checkbox)s'
    
    def __init__(self, file_widget=None,
                 attrs=None, template=None):
        if template is not None:
            self.template = template
        file_widget = file_widget or self.default_file_widget_class()
        super(ClearableFileInput, self).__init__(
            widgets=[file_widget, forms.CheckboxInput()],
            attrs=attrs)

    def decompress(self, value):
        # the clear checkbox is never initially checked
        self.value = value
        return [value, None]

    def format_output(self, rendered_widgets):
        if self.value:
            return self.template % {'input': rendered_widgets[0],
                                    'checkbox': rendered_widgets[1]}
        return rendered_widgets[0]

class FakeEmptyFieldFile(object):
    """
    A fake FieldFile that will convice a FileField model field to
    actually replace an existing file name with an empty string.
    
    FileFild.save_form_data only overwrites its instance data if the
    incoming form data evaluates to True in a boolean context (because
    an empty file input is assumed to mean "no change"). We want to be
    able to clear it without requiring the use of a model FileField
    subclass (keeping things at the form level only). In order to do
    this we need our form field to return a value that evaluates to
    True in a boolean context, but to the empty string when coerced to
    unicode. This object fulfills that requirement.

    It also needs the _committed attribute to satisfy the test in
    FileField.pre_save.

    This is, of course, hacky and fragile, and depends on internal
    knowledge of the FileField and FieldFile classes. But it will
    serve until Django FileFields acquire a native ability to be
    cleared (ticket 7048).

    """
    def __unicode__(self):
        return u''
    _committed = True

class ClearableFileField(forms.MultiValueField):
    default_file_field_class = forms.FileField
    widget = ClearableFileInput
    
    def __init__(self, file_field=None, *args, **kwargs):
        file_field = file_field or self.default_file_field_class(*args,
                                                                  **kwargs)
        fields = (file_field, forms.BooleanField(required=False))
        kwargs['required'] = file_field.required
        kwargs['widget'] = self.widget(file_widget=file_field.widget)
        super(ClearableFileField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list[1] and not data_list[0]:
            return FakeEmptyFieldFile()
        return data_list[0]

