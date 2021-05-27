# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-12-03 20:15
from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.utils.timezone

from matchmaker.matchmaker_utils import get_submission_json_for_external_match

RESULT_FIELDS = [
    "guid",
    "created_date",
    "last_modified_date",
    "result_data",
    "we_contacted",
    "host_contacted",
    "deemed_irrelevant",
    "flag_for_analysis",
    "comments",
    "match_removed",
    "created_by_id",
    "last_modified_by_id",
]
CONTACT_NOTE_FIELDS = [
    "guid",
    "created_date",
    "last_modified_date",
    "institution",
    "comments",
    "created_by_id",
]

# For a few individuals that have duplicate IDs across project, the same id got used twice for mathmaker.
# This was actually a bug, as matchmaker replaces when it recieves a duplicate ID
DUPLICATED_SUBMISSION_IDS = {
    "89dcbe5e752737cb1991dd34dfae68c1",
    "BON_UC499_1_1",
    "MAN_1024-01_2",
    "WAL_CH2900_CH2901",
    "WAL_CH5200_CH5201",
    "WAL_CH5700_CH5701",
    "WAL_DC2200_DC2201",
    "WAL_DC3500_DC3501",
    "WAL_LIS4900_LIS4901",
    "WAL_PAC2800_PAC2801",
}


def bulk_copy_models(
    db_alias, source_model, dest_model, fields, field_process_funcs=None, db_filter=None
):
    field_process_funcs = field_process_funcs or {}
    all_source_models = source_model.objects.using(db_alias)
    if db_filter:
        all_source_models = all_source_models.filter(db_filter)
    all_source_models = all_source_models.all()
    if all_source_models:
        print(
            "Copying {} {} to {}".format(
                all_source_models.count(), source_model.__name__, dest_model.__name__
            )
        )
        new_models = [
            dest_model(
                **{
                    field: field_process_funcs.get(field, getattr)(model, field)
                    for field in fields
                }
            )
            for model in all_source_models
        ]
        dest_model.objects.bulk_create(new_models)


def migrate_submissions(apps, schema_editor):
    Individual = apps.get_model("seqr", "Individual")
    MatchmakerSubmission = apps.get_model("matchmaker", "MatchmakerSubmission")
    db_alias = schema_editor.connection.alias

    fields = [
        "guid",
        "created_date",
        "last_modified_date",
        "submission_id",
        "label",
        "contact_name",
        "contact_href",
        "features",
        "genomic_features",
        "deleted_date",
        "created_by_id",
        "deleted_by_id",
        "individual_id",
    ]
    found_duplicates = set()

    def get_submitted_data_field(model, field):
        value = model.mme_submitted_data["patient"]
        for field_key in field.split("_"):
            value = value[field_key]
        return value

    def get_submission_id(model, field):
        submission_id = get_submitted_data_field(model, "id")
        if submission_id in DUPLICATED_SUBMISSION_IDS:
            if submission_id in found_duplicates:
                submission_id = "{}_b".format(submission_id)
            else:
                found_duplicates.add(submission_id)
        return submission_id

    def get_genomic_features(model, field):
        return model.mme_submitted_data["patient"]["genomicFeatures"]

    field_process_funcs = {
        "guid": lambda model, field: model.guid.replace("I", "MS")[:30],
        "created_date": lambda model, field: model.mme_submitted_date,
        "deleted_date": lambda model, field: model.mme_deleted_date,
        "last_modified_date": lambda model, field: model.mme_deleted_date
        or model.mme_submitted_date,
        "deleted_by_id": lambda model, field: model.mme_deleted_by_id,
        "individual_id": lambda model, field: model.id,
        "submission_id": get_submission_id,
        "label": get_submitted_data_field,
        "contact_name": get_submitted_data_field,
        "contact_href": get_submitted_data_field,
        "features": get_submitted_data_field,
        "genomic_features": get_genomic_features,
    }

    bulk_copy_models(
        db_alias,
        Individual,
        MatchmakerSubmission,
        fields,
        field_process_funcs=field_process_funcs,
        db_filter=models.Q(mme_submitted_data__isnull=False),
    )


def copy_results(apps, schema_editor):
    SeqrResult = apps.get_model("seqr", "MatchmakerResult")
    MatchmakerResult = apps.get_model("matchmaker", "MatchmakerResult")
    db_alias = schema_editor.connection.alias

    field_process_funcs = {
        "submission": lambda model, field: model.individual.matchmakersubmission
    }
    fields = RESULT_FIELDS + list(field_process_funcs.keys())
    bulk_copy_models(
        db_alias,
        SeqrResult,
        MatchmakerResult,
        fields,
        field_process_funcs=field_process_funcs,
    )


def copy_contact_notes(apps, schema_editor):
    SeqrContactNotes = apps.get_model("seqr", "MatchmakerContactNotes")
    MatchmakerContactNotes = apps.get_model("matchmaker", "MatchmakerContactNotes")
    db_alias = schema_editor.connection.alias

    bulk_copy_models(
        db_alias, SeqrContactNotes, MatchmakerContactNotes, CONTACT_NOTE_FIELDS
    )


def reverse_migrate_submissions(apps, schema_editor):
    MatchmakerSubmission = apps.get_model("matchmaker", "MatchmakerSubmission")
    db_alias = schema_editor.connection.alias

    for submission in (
        MatchmakerSubmission.objects.using(db_alias)
        .all()
        .prefetch_related("individual")
    ):
        ind = submission.individual
        ind.mme_deleted_by_id = submission.deleted_by_id
        ind.mme_deleted_date = submission.deleted_date
        ind.mme_submitted_date = submission.created_date
        ind.mme_submitted_data = get_submission_json_for_external_match(submission)
        ind.save()


def reverse_copy_results(apps, schema_editor):
    SeqrResult = apps.get_model("seqr", "MatchmakerResult")
    MatchmakerResult = apps.get_model("matchmaker", "MatchmakerResult")
    db_alias = schema_editor.connection.alias

    field_process_funcs = {
        "individual_id": lambda model, field: model.submission.individual_id
    }
    fields = RESULT_FIELDS + field_process_funcs.keys()
    bulk_copy_models(
        db_alias,
        MatchmakerResult,
        SeqrResult,
        fields,
        field_process_funcs=field_process_funcs,
        db_filter=models.Q(submission__isnull=False),
    )


def reverese_copy_contact_notes(apps, schema_editor):
    SeqrContactNotes = apps.get_model("seqr", "MatchmakerContactNotes")
    MatchmakerContactNotes = apps.get_model("matchmaker", "MatchmakerContactNotes")
    db_alias = schema_editor.connection.alias

    bulk_copy_models(
        db_alias, MatchmakerContactNotes, SeqrContactNotes, CONTACT_NOTE_FIELDS
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("seqr", "0001_squashed_0067_remove_project_custom_reference_populations"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MatchmakerSubmission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("guid", models.CharField(db_index=True, max_length=30, unique=True)),
                (
                    "created_date",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "last_modified_date",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "submission_id",
                    models.CharField(db_index=True, max_length=255, unique=True),
                ),
                ("label", models.CharField(blank=True, max_length=255, null=True)),
                ("contact_name", models.TextField(default="Samantha Baxter")),
                (
                    "contact_href",
                    models.TextField(
                        default="mailto:matchmaker@populationgenomics.org.au"
                    ),
                ),
                ("features", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                (
                    "genomic_features",
                    django.contrib.postgres.fields.jsonb.JSONField(null=True),
                ),
                ("deleted_date", models.DateTimeField(null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "deleted_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "individual",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="seqr.Individual",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MatchmakerContactNotes",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("guid", models.CharField(db_index=True, max_length=30, unique=True)),
                (
                    "created_date",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "last_modified_date",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "institution",
                    models.CharField(db_index=True, max_length=200, unique=True),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MatchmakerResult",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("guid", models.CharField(db_index=True, max_length=30, unique=True)),
                (
                    "created_date",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "last_modified_date",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                ("result_data", django.contrib.postgres.fields.jsonb.JSONField()),
                ("we_contacted", models.BooleanField(default=False)),
                ("host_contacted", models.BooleanField(default=False)),
                ("deemed_irrelevant", models.BooleanField(default=False)),
                ("flag_for_analysis", models.BooleanField(default=False)),
                ("comments", models.TextField(blank=True, null=True)),
                ("match_removed", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "last_modified_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="matchmaker.MatchmakerSubmission",
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MatchmakerIncomingQuery",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("guid", models.CharField(db_index=True, max_length=30, unique=True)),
                (
                    "created_date",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "last_modified_date",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                ("institution", models.CharField(max_length=255)),
                ("patient_id", models.CharField(null=True, max_length=255)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="matchmakerresult",
            name="originating_query",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="matchmaker.MatchmakerIncomingQuery",
            ),
        ),
        migrations.RunPython(
            migrate_submissions, reverse_code=reverse_migrate_submissions
        ),
        migrations.RunPython(copy_results, reverse_code=reverse_copy_results),
        migrations.RunPython(
            copy_contact_notes, reverse_code=reverese_copy_contact_notes
        ),
    ]
