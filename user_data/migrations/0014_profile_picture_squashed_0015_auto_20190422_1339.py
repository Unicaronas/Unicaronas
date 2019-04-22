# Generated by Django 2.1.7 on 2019-04-22 16:56

from django.db import migrations
import project.validators.image
import user_data.models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user_data', '0013_auto_20190417_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='picture',
            field=versatileimagefield.fields.VersatileImageField(blank=True, upload_to=user_data.models.get_pic_path, validators=[project.validators.image.MinImageDimensionsValidator(256, 256), project.validators.image.MaxImageDimensionsValidator(2048, 2048), project.validators.image.SquareImageValidator()], verbose_name='Foto de perfil'),
        ),
    ]