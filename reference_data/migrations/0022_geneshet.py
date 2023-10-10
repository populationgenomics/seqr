# Generated by Django 3.2.18 on 2023-10-10 20:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reference_data', '0021_auto_20221031_2049'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneShet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_mean', models.FloatField()),
                ('gene', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference_data.geneinfo')),
            ],
        ),
    ]
