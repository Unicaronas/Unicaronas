# Generated by Django 2.1.1 on 2018-10-13 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alarms', '0002_auto_20181013_0006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alarm',
            name='auto_approve',
            field=models.NullBooleanField(verbose_name='Aprovação automática de passageiros'),
        ),
    ]