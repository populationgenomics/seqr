# Generated by Django 3.1.3 on 2020-12-21 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seqr', '0018_auto_20201202_1553'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='locuslist',
            options={},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'permissions': (('can_view', 'can_view'), ('can_edit', 'can_edit'))},
        ),
        migrations.RemoveField(
            model_name='project',
            name='owners_group',
        ),
    ]
