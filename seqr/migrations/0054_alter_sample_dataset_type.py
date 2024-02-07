# Generated by Django 3.2.18 on 2023-09-15 14:54

from django.db import migrations, models

OLD_DT = 'VARIANTS'
NEW_DT = 'SNV_INDEL'

def update_dataset_type(is_forward):
    def _update_dataset_type(apps, schema_editor):
        Sample = apps.get_model('seqr', 'Sample')
        db_alias = schema_editor.connection.alias

        samples = Sample.objects.using(db_alias).filter(dataset_type=OLD_DT if is_forward else NEW_DT)
        if samples:
            print(f'Updating {len(samples)} samples')
            samples.update(dataset_type=NEW_DT if is_forward else OLD_DT)
            print('Done')
    return _update_dataset_type


class Migration(migrations.Migration):

    dependencies = [
        ('seqr', '0053_auto_20230810_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='dataset_type',
            field=models.CharField(choices=[(NEW_DT, 'Variant Calls'), ('SV', 'SV Calls'), ('MITO', 'Mitochondria calls')], max_length=10),
        ),
        migrations.RunPython(update_dataset_type(True), reverse_code=update_dataset_type(False)),
    ]
