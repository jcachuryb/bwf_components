# Generated by Django 5.2 on 2025-06-25 07:44

import django.db.models.deletion
import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bwf_forms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApprovalUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'User',
                'constraints': [models.UniqueConstraint(django.db.models.functions.text.Lower('email'), name='approvals_unique_email')],
            },
        ),
        migrations.CreateModel(
            name='BWF_Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system_name', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': 'BWF Role',
                'constraints': [models.UniqueConstraint(fields=('system_name', 'name'), name='approvals_unique_name_system')],
            },
        ),
        migrations.CreateModel(
            name='FormApproval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval_id', models.CharField(max_length=100, unique=True)),
                ('workflow_instance_id', models.IntegerField()),
                ('component_instance_id', models.IntegerField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('decision_due_date', models.DateTimeField(blank=True, null=True)),
                ('form_version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bwf_forms.bwfformversion')),
            ],
        ),
        migrations.CreateModel(
            name='ApprovalRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('approve', 'Approve'), ('reject', 'Reject')], default='approve', max_length=20)),
                ('approved', models.BooleanField(default=False)),
                ('date_approved', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bwf_approvals.approvaluser')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bwf_approvals.bwf_role')),
                ('approval', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bwf_approvals.formapproval')),
            ],
        ),
    ]
