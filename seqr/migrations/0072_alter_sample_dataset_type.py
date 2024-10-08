# Generated by Django 4.2.13 on 2024-08-14 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seqr', '0071_igvsample_index_file_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='dataset_type',
            field=models.CharField(choices=[('SNV_INDEL', 'Variant Calls'), ('SV', 'SV Calls'), ('MITO', 'Mitochondria calls')], max_length=13),
        ),
    ]
