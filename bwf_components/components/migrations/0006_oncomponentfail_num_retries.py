# Generated by Django 5.0.11 on 2025-02-19 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('components', '0005_alter_oncomponentfail_component_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='oncomponentfail',
            name='num_retries',
            field=models.SmallIntegerField(default=0),
        ),
    ]
