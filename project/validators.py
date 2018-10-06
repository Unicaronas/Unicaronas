from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator


class MaxImageDimensionsValidator(BaseValidator):
    message = 'Sua imagem pode ter no máximo %(limit_height)s px de altura e %(limit_width)s px de largura (ela tem %(show_height)s por %(show_width)s).'
    code = 'image_max_dimensions'

    def __init__(self, limit_width, limit_height, message=None):
        self.limit_height = limit_height
        self.limit_width = limit_width
        if message:
            self.message = message

    def __call__(self, value):
        width, height = get_image_dimensions(value.file)
        cleaned_width, cleaned_height = self.clean(width, height)
        params = {'limit_height': self.limit_height, 'limit_width': self.limit_width, 'show_height': cleaned_height, 'show_width': cleaned_width, 'height': height, 'width': width}
        if self.compare((cleaned_width, cleaned_height), (self.limit_width, self.limit_height)):
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.limit_height == other.limit_height and
            self.limit_width == other.limit_width and
            self.message == other.message and
            self.code == other.code
        )

    def compare(self, cleaned, limit):
        return cleaned[0] > limit[0] or cleaned[1] > limit[1]

    def clean(self, width, height):
        return width, height


class MinImageDimensionsValidator(MaxImageDimensionsValidator):
    message = 'Sua imagem pode ter no mínimo %(limit_height)s px de altura e %(limit_width)s px de largura (ela tem %(show_height)s por %(show_width)s).'
    code = 'image_min_dimensions'

    def compare(self, cleaned, limit):
        return cleaned[0] < limit[0] or cleaned[1] < limit[1]


class SquareImageValidator(BaseValidator):
    message = 'Sua imagem deve ser quadrada (ela tem %(show_height)s por %(show_width)s px).'
    code = 'image_square'

    def __init__(self, message=None):
        if message:
            self.message = message

    def __call__(self, value):
        width, height = get_image_dimensions(value.file)
        cleaned_width, cleaned_height = self.clean(width, height)
        params = {'show_height': cleaned_height, 'show_width': cleaned_width, 'height': height, 'width': width}
        if self.compare((cleaned_width, cleaned_height)):
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.message == other.message and
            self.code == other.code
        )

    def compare(self, cleaned):
        return cleaned[0] != cleaned[1]

    def clean(self, width, height):
        return width, height
