# Generated by Django 5.0.11 on 2025-03-21 00:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0015_alter_workflowversion_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workflowinstance',
            name='workflow',
        ),
    ]
