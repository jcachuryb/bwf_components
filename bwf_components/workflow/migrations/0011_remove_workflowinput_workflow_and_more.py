# Generated by Django 5.0.11 on 2025-03-18 03:20

import bwf_components.workflow.models
import django.core.files.storage
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0010_remove_componentinstance_component_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workflowinput',
            name='workflow',
        ),
        migrations.RemoveField(
            model_name='workflow',
            name='main_cluster',
        ),
        migrations.CreateModel(
            name='WorkflowVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_number', models.CharField(max_length=15)),
                ('version_name', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_edition', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('workflow_file', models.FileField(blank=True, max_length=1000, null=True, storage=django.core.files.storage.FileSystemStorage(location='/data/data/projects/spatial-layer-monitor/private-media'), upload_to=bwf_components.workflow.models.updaload_to_workflow_edition_path)),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='workflow.workflow')),
            ],
        ),
        migrations.DeleteModel(
            name='VariableValue',
        ),
        migrations.DeleteModel(
            name='WorkflowInput',
        ),
    ]
