# Generated by Django 3.0.7 on 2020-10-19 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('build', '0019_auto_20201019_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='build',
            name='title',
            field=models.CharField(help_text='Brief description of the build', max_length=100, verbose_name='Description'),
        ),
    ]
