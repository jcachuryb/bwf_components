# Generated by Django 5.0.11 on 2025-02-18 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('components', '0003_rename_component_workflowcomponent_definition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='componentdefinition',
            name='base_output',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
