# Generated by Django 5.0.11 on 2025-03-05 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0008_alter_variablevalue_data_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='componentinstance',
            name='parent_action',
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='component_definition',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='options',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='plugin_id',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='plugin_version',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='workflow',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
