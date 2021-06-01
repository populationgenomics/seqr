# Generated by Django 3.1.6 on 2021-04-20 15:30
from collections import defaultdict
from django.contrib.postgres.aggregates import StringAgg
from django.db import migrations, models
from django.db.models.functions import Concat
from django.utils import timezone
import logging
from seqr.utils.logging_utils import log_model_update, log_model_bulk_update

logger = logging.getLogger(__name__)


def _update_tag_type(tag_type, json):
    for field, val in json.items():
        setattr(tag_type, field, val)
    tag_type.last_modified_date = timezone.now()
    log_model_update(logger, tag_type, user=None, update_type='update', update_fields=list(json.keys()) + ['last_modified_date'])
    tag_type.save()

def _bulk_update_tags(tag_type, json, tag_model_q):
    tag_models = tag_model_q.filter(variant_tag_type=tag_type)
    log_model_bulk_update(logger, tag_models, user=None, update_type='update', update_fields=list(json.keys()))
    tag_models.update(**json)
    return tag_models


def merge_project_sanger_tags(apps, schema_editor):
    VariantTagType = apps.get_model("seqr", "VariantTagType")
    VariantTag = apps.get_model("seqr", "VariantTag")
    db_alias = schema_editor.connection.alias
    project_sanger_tag_types = VariantTagType.objects.using(db_alias).filter(name='Sanger in progress')
    if project_sanger_tag_types:
        logger.info('Merging "Sanger in progress" tags from {} projects'.format(len(project_sanger_tag_types)))
        main_tag_type = project_sanger_tag_types[0]
        _update_tag_type(main_tag_type, {'project': None})

        for sanger_tag_type in project_sanger_tag_types[1:]:
            _bulk_update_tags(sanger_tag_type, {'variant_tag_type': main_tag_type}, VariantTag.objects.using(db_alias))
            log_model_update(logger, sanger_tag_type, user=None, update_type='delete')
            sanger_tag_type.delete()


SANGER_TAGS = {
    'Send for Sanger validation': 'Send for validation',
    'Sanger in progress': 'Validation in progress',
    'Sanger validated': 'Validated',
    'Sanger did not confirm': 'Validation did not confirm',
    'Sanger troubleshooting': 'Validation troubleshooting',
}

VALIDATION_TAGS = {
    'Test segregation': ('Send for validation', 'Segregation'),
    'Segregation validated': ('Validated', 'Segregation'),
    'Segregation did not confirm': ('Validation did not confirm', 'Segregation'),
    'Validate SV': ('Send for validation', 'SV'),
    'SV validated': ('Validated', 'SV'),
    'SV did not confirm': ('Validation did not confirm', 'SV')
}

def update_validation_tag_types(apps, schema_editor):
    VariantTagType = apps.get_model("seqr", "VariantTagType")
    VariantTag = apps.get_model("seqr", "VariantTag")
    db_alias = schema_editor.connection.alias
    variant_tag_q = VariantTag.objects.using(db_alias)

    sanger_tag_types = VariantTagType.objects.using(db_alias).filter(project__isnull=True, name__in=SANGER_TAGS.keys())
    if not sanger_tag_types:
        logger.info('No sanger tags found, skipping validation tag migration')
        return

    tag_type_map = {}
    for tag_type in sanger_tag_types:
        new_name = SANGER_TAGS[tag_type.name]
        _update_tag_type(tag_type, {'name': new_name, 'description': None, 'metadata_title': 'Test Type(s)'})
        _bulk_update_tags(tag_type, {'metadata': 'Sanger'}, variant_tag_q)
        tag_type_map[new_name] = tag_type

    validation_tag_types = VariantTagType.objects.using(db_alias).filter(project__isnull=True, name__in=VALIDATION_TAGS.keys())
    for tag_type in validation_tag_types:
        new_name, meta_name = VALIDATION_TAGS[tag_type.name]
        new_tag_type = tag_type_map[new_name]
        _bulk_update_tags(tag_type, {'variant_tag_type': new_tag_type, 'metadata': meta_name}, variant_tag_q)


def revert_validation_tag_types(apps, schema_editor):
    VariantTagType = apps.get_model("seqr", "VariantTagType")
    VariantTag = apps.get_model("seqr", "VariantTag")
    db_alias = schema_editor.connection.alias

    tag_names = list(SANGER_TAGS.values()) + list(VALIDATION_TAGS.keys())
    tag_type_lookup = {
        t.name: t for t in VariantTagType.objects.using(db_alias).filter(project__isnull=True, name__in=tag_names)}

    for old_tag_name, (new_tag_name, meta_name) in VALIDATION_TAGS.items():
        tags_q = VariantTag.objects.using(db_alias).filter(metadata=meta_name)
        _bulk_update_tags(tag_type_lookup[new_tag_name], {'variant_tag_type': tag_type_lookup[old_tag_name]}, tags_q)

    for old_name, new_name in SANGER_TAGS.items():
        _update_tag_type(tag_type_lookup[new_name], {'name': old_name})


def remove_unused_validation_tag_types(apps, schema_editor):
    VariantTagType = apps.get_model("seqr", "VariantTagType")
    db_alias = schema_editor.connection.alias
    tag_types = VariantTagType.objects.using(db_alias).filter(project__isnull=True, name__in=VALIDATION_TAGS.keys())
    if tag_types:
        log_model_bulk_update(logger, tag_types, user=None, update_type='delete')
        tag_types.delete()


def create_validation_tags(apps, schema_editor):
    VariantTagType = apps.get_model("seqr", "VariantTagType")
    db_alias = schema_editor.connection.alias

    for old_tag_name in VALIDATION_TAGS.keys():
        VariantTagType.objects.using(db_alias).create(name=old_tag_name, guid=old_tag_name)


def merge_duplicate_tags(apps, schema_editor):
    VariantTag = apps.get_model("seqr", "VariantTag")
    db_alias = schema_editor.connection.alias

    updated_tags = VariantTag.objects.using(db_alias).filter(variant_tag_type__name__in=SANGER_TAGS.values()).annotate(
        group_id=Concat('variant_tag_type__guid', StringAgg('saved_variants__guid', ',', ordering='saved_variants__guid')))
    if not updated_tags:
        logger.info('No updated tags found, skipping validation tag merging')
        return

    grouped_tags = defaultdict(list)
    for tag in updated_tags:
        grouped_tags[tag.group_id].append(tag)
    duplicate_tags = [tags for tags in grouped_tags.values() if len(tags) > 1]

    logger.info('Merging {} sets of tags'.format(len(duplicate_tags)))
    for tags in duplicate_tags:
        log_model_update(logger, tags[0], user=None, update_type='update', update_fields=['metadata'])
        tags[0].metadata = ', '.join([t.metadata for t in tags])
        tags[0].save()
        for tag in tags[1:]:
            log_model_update(logger, tag, user=None, update_type='delete')
            tag.delete()


def split_duplicate_tags(apps, schema_editor):
    VariantTag = apps.get_model("seqr", "VariantTag")
    db_alias = schema_editor.connection.alias

    duplicate_tags = VariantTag.objects.using(db_alias).filter(metadata__contains=',')
    logger.info('Splitting {} sets of tags'.format(len(duplicate_tags)))
    for tag in duplicate_tags:
        meta_names = tag.metadata.split(', ')
        tag.metadata = meta_names[0]
        tag.save()
        saved_variants = tag.saved_variants.all()
        for meta_name in meta_names[1:]:
            tag.pk = None # creates a new object with the same properties as the original model
            tag.guid = tag.guid[:18] + meta_name
            tag.metadata = meta_name
            tag.save()
            tag.saved_variants.set(saved_variants)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('seqr', '0023_auto_20210304_2315'),
    ]

    operations = [
        migrations.AddField(
            model_name='varianttag',
            name='metadata',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='varianttagtype',
            name='metadata_title',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.RunPython(merge_project_sanger_tags, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(update_validation_tag_types, reverse_code=revert_validation_tag_types),
        migrations.RunPython(remove_unused_validation_tag_types, reverse_code=create_validation_tags),
        migrations.RunPython(merge_duplicate_tags, reverse_code=split_duplicate_tags),
    ]
