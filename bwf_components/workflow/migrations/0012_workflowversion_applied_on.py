# Generated by Django 5.0.11 on 2025-03-19 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0011_remove_workflowinput_workflow_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflowversion',
            name='applied_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
