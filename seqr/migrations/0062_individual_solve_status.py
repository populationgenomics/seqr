# Generated by Django 3.2.23 on 2024-04-01 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seqr', '0061_auto_20240313_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='individual',
            name='solve_status',
            field=models.CharField(blank=True, choices=[('S', 'Solved'), ('P', 'Partially solved'), ('B', 'Probably solved'), ('U', 'Unsolved')], max_length=1, null=True),
        ),
    ]
