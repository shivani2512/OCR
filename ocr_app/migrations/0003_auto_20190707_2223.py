# Generated by Django 2.2.3 on 2019-07-07 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ocr_app', '0002_auto_20190707_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=255, unique=True, verbose_name='Email Address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(default='', max_length=250),
        ),
    ]
