import qrcode

from django import forms

from .widgets import Base64ImageWidget, ImageWidget


class ImageField(forms.fields.Field):
    widget = ImageWidget

    def __init__(self, *args, **kwargs):
        self.image_alt_text = kwargs.pop('image_alt_text', '')
        super().__init__(*args, **kwargs)
        self.widget.attrs['alt'] = self.image_alt_text


class ReadOnlyImageField(forms.ImageField):
    def clean(self, data, initial=None):
        return ''


class QRCodeImageField(ReadOnlyImageField):
    widget = Base64ImageWidget

    def prepare_value(self, value):
        instance = qrcode.QRCode()
        instance.add_data(value)
        instance.make(fit=True)

        qrcode_image = instance.make_image()

        size = qrcode_image.height / 2

        self.widget.attrs['height'] = size
        self.widget.attrs['width'] = size

        return qrcode_image
