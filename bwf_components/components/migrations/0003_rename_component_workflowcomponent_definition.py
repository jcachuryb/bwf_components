# Generated by Django 5.0.11 on 2025-02-18 07:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('components', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='workflowcomponent',
            old_name='component',
            new_name='definition',
        ),
    ]
