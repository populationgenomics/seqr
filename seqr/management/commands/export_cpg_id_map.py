from django.core.management.base import BaseCommand

import csv
from datetime import datetime
from seqr.models import Sample

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Export a tsv file with the cpg_id to individual/family/project_guid mappings"
    )

    def handle(self, *args, **options):
        outfile_name = (
            f'/app/seqr/cpg_id_map_{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}'
        )

        # Get all the active samples
        samples = Sample.objects.filter(is_active=True)

        logger.info(f"Exporting {len(samples)} active samples to a tsv file")

        sample_id_to_project_guid = {}
        sample_id_to_family_guid = {}
        sample_id_to_individual_id = {}

        for sample in samples:
            sample_id = sample.sample_id
            individual_id = sample.individual.individual_id
            family_guid = sample.individual.family.guid
            project_guid = sample.individual.family.project.guid

            if sample_id not in sample_id_to_project_guid:
                sample_id_to_project_guid[sample_id] = project_guid
            if sample_id not in sample_id_to_family_guid:
                sample_id_to_family_guid[sample_id] = family_guid
            if sample_id not in sample_id_to_individual_id:
                sample_id_to_individual_id[sample_id] = individual_id

        # Write the sample_id_to_individual/family/project_guid dicts to a tsv file
        with open(outfile_name, "w") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(["cpg_id", "individual_id", "family_guid", "project_guid"])
            for sample_id, project_guid in sample_id_to_project_guid.items():
                writer.writerow(
                    [
                        sample_id,
                        sample_id_to_individual_id[sample_id],
                        sample_id_to_family_guid[sample_id],
                        project_guid,
                    ]
                )

        logger.info(
            f"Exported mappings for {len(samples)} active samples to {outfile_name}"
        )
