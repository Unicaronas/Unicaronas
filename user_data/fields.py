from django import forms
from django.core.validators import FileExtensionValidator
from croppie.fields import CroppieField
from croppie.widgets import CroppieImageRatioWidget, CroppieWidget


class CustomCroppieImageRatioWidget(CroppieImageRatioWidget):
    def __init__(self, options, *args, **kwargs):
        widgets = (
            CroppieWidget(
                options=options,
                attrs={
                    'data-validation': 'required size mime',
                    'data-validation-max-size': '5M',
                    'data-validation-allowing': 'jpg, png',
                    'accept': '.jpeg,.jpg,.png'
                }
            ),
            forms.HiddenInput(),
            forms.HiddenInput(),
            forms.HiddenInput(),
            forms.HiddenInput(),
        )
        super(CroppieImageRatioWidget, self).__init__(
            widgets=widgets,
            *args, **kwargs
        )


class SquareCroppieField(CroppieField):
    """Always crop square images"""

    def __init__(self, options={}, widget_kwargs={}, widget=None, *args, **kwargs):
        widget = CustomCroppieImageRatioWidget(
            options=options,
            **widget_kwargs
        )
        fields = (
            forms.FileField(),
            forms.CharField(),
            forms.CharField(),
            forms.CharField(),
            forms.CharField(),
        )
        super(CroppieField, self).__init__(
            fields=fields, widget=widget, *args, **kwargs)

    def crop_image(self, data_image, ratio):
        ratio[3] = ratio[1] + ratio[2] - ratio[0]
        return super().crop_image(data_image, ratio)
