# Generated by Django 2.1.7 on 2019-04-02 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_data', '0010_auto_20190402_1730'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentproof',
            name='proof_scan_id',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]