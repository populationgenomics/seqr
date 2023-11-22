from django.urls.base import reverse
from django.utils.dateparse import parse_datetime
import json
import mock
import pytz
import responses
from settings import AIRTABLE_URL

from seqr.models import Project, SavedVariant
from seqr.views.apis.report_api import seqr_stats, get_category_projects, discovery_sheet, anvil_export, gregor_export
from seqr.views.utils.test_utils import AuthenticationTestCase, AnvilAuthenticationTestCase, AirtableTest


PROJECT_GUID = 'R0001_1kg'
NON_PROJECT_GUID ='NON_GUID'
PROJECT_EMPTY_GUID = 'R0002_empty'
COMPOUND_HET_PROJECT_GUID = 'R0003_test'
NO_ANALYST_PROJECT_GUID = 'R0004_non_analyst_project'

EXPECTED_DISCOVERY_SHEET_ROW = \
    {'project_guid': 'R0001_1kg', 'pubmed_ids': '34415322; 33665635', 'posted_publicly': '',
     'solved': 'TIER 1 GENE', 'head_or_neck': 'N', 'analysis_complete_status': 'complete',
     'cardiovascular_system': 'N', 'n_kindreds_overlapping_sv_similar_phenotype': '2',
     'biochemical_function': 'Y', 'omim_number_post_discovery': '615120,615123',
     'genome_wide_linkage': 'NA 2', 'metabolism_homeostasis': 'N', 'growth': 'N',
     't0': '2017-02-05T06:42:55.397Z', 'months_since_t0': 38, 'sample_source': 'CMG',
     'integument': 'N', 'voice': 'N', 'skeletal_system': 'N',
     'expected_inheritance_model': 'Autosomal recessive inheritance',
     'extras_variant_tag_list': ['21-3343353-GAGA-G  RP11  tier 1 - novel gene and phenotype'],
     'protein_interaction': 'N', 'n_kindreds': '1', 'num_individuals_sequenced': 3,
     'musculature': 'Y', 'sequencing_approach': 'WES', 'neoplasm': 'N',
     'collaborator': '1kg project n\xe5me with uni\xe7\xf8de',
     'actual_inheritance_model': 'de novo', 'novel_mendelian_gene': 'Y',
     'endocrine_system': 'N', 'patient_cells': 'N', 'komp_early_release': 'N',
     'connective_tissue': 'N', 'prenatal_development_or_birth': 'N', 'rescue': 'N',
     'family_guid': 'F000001_1', 'immune_system': 'N',
     'analysis_summary': '*\r\nF\u00e5mily analysis summ\u00e5ry.\r\n*; Some additional follow up',
     'gene_count': 'NA', 'gene_id': 'ENSG00000135953', 'abdomen': 'N', 'limbs': 'N',
     'blood': 'N', 'phenotype_class': 'KNOWN', 'submitted_to_mme': 'Y',
     'n_unrelated_kindreds_with_causal_variants_in_gene': '3',
     'row_id': 'F000001_1ENSG00000135953', 'eye_defects': 'N', 'omim_number_initial': '12345',
     'p_value': 'NA', 'respiratory': 'N', 'nervous_system': 'Y', 'ear_defects': 'N',
     'thoracic_cavity': 'N', 'non_patient_cell_model': 'N',
     't0_copy': '2017-02-05T06:42:55.397Z', 'extras_pedigree_url': '/media/ped_1.png',
     'family_id': '1', 'genitourinary_system': 'N', 'coded_phenotype': 'myopathy',
     'animal_model': 'N', 'non_human_cell_culture_model': 'N', 'expression': 'N',
     'gene_name': 'RP11', 'breast': 'N'}

EXPECTED_DISCOVERY_SHEET_COMPOUND_HET_ROW = {
    'project_guid': 'R0003_test', 'pubmed_ids': '', 'posted_publicly': '', 'solved': 'TIER 1 GENE', 'head_or_neck': 'N',
    'analysis_complete_status': 'complete', 'cardiovascular_system': 'Y',
    'n_kindreds_overlapping_sv_similar_phenotype': 'NA', 'biochemical_function': 'N', 'omim_number_post_discovery': 'NA',
    'genome_wide_linkage': 'NA', 'metabolism_homeostasis': 'N', 'growth': 'N', 't0': '2017-02-05T06:42:55.397Z',
    'months_since_t0': 38, 'sample_source': 'CMG', 'integument': 'N', 'voice': 'N', 'skeletal_system': 'N',
    'expected_inheritance_model': 'multiple', 'num_individuals_sequenced': 2, 'sequencing_approach': 'REAN',
    'extras_variant_tag_list': ['1-248367227-TC-T  OR4G11P  tier 1 - novel gene and phenotype',
        'prefix_19107_DEL  OR4G11P  tier 1 - novel gene and phenotype'], 'protein_interaction': 'N', 'n_kindreds': '1',
    'neoplasm': 'N', 'collaborator': 'Test Reprocessed Project', 'actual_inheritance_model': 'AR-comphet',
    'novel_mendelian_gene': 'Y', 'endocrine_system': 'N', 'komp_early_release': 'N', 'connective_tissue': 'N',
    'prenatal_development_or_birth': 'N', 'rescue': 'N', 'family_guid': 'F000012_12', 'immune_system': 'N',
    'analysis_summary': '', 'gene_count': 'NA', 'gene_id': 'ENSG00000240361', 'abdomen': 'N', 'limbs': 'N',
    'phenotype_class': 'New', 'submitted_to_mme': 'Y', 'n_unrelated_kindreds_with_causal_variants_in_gene': '1',
    'blood': 'N',  'row_id': 'F000012_12ENSG00000240361', 'eye_defects': 'N', 'omim_number_initial': 'NA',
    'p_value': 'NA', 'respiratory': 'N', 'nervous_system': 'N', 'ear_defects': 'N', 'thoracic_cavity': 'N',
    'non_patient_cell_model': 'N', 't0_copy': '2017-02-05T06:42:55.397Z', 'extras_pedigree_url': '',
    'family_id': '12', 'genitourinary_system': 'N', 'coded_phenotype': '', 'animal_model': 'N', 'expression': 'N',
    'non_human_cell_culture_model': 'N', 'gene_name': 'OR4G11P', 'breast': 'N', 'musculature': 'N', 'patient_cells': 'N',}

AIRTABLE_SAMPLE_RECORDS = {
  "records": [
    {
      "id": "rec2B6OGmQpAkQW3s",
      "fields": {
        "SeqrCollaboratorSampleID": "VCGS_FAM203_621_D1",
        "CollaboratorSampleID": "NA19675",
        "Collaborator": ["recW24C2CJW5lT64K"],
        "dbgap_study_id": "dbgap_stady_id_1",
        "dbgap_subject_id": "dbgap_subject_id_1",
        "dbgap_sample_id": "SM-A4GQ4",
        "SequencingProduct": [
          "Mendelian Rare Disease Exome"
        ],
        "dbgap_submission": [
          "WES",
          "Array"
        ]
      },
      "createdTime": "2019-09-09T19:21:12.000Z"
    },
    {
      "id": "rec2Nkg10N1KssPc3",
      "fields": {
        "SeqrCollaboratorSampleID": "HG00731",
        "CollaboratorSampleID": "NA20885",
        "Collaborator": ["reca4hcBnbA2cnZf9"],
        "dbgap_study_id": "dbgap_stady_id_2",
        "dbgap_subject_id": "dbgap_subject_id_2",
        "dbgap_sample_id": "SM-JDBTT",
        "SequencingProduct": [
          "Standard Germline Exome v6 Plus GSA Array"
        ],
        "dbgap_submission": [
          "WES",
          "Array"
        ]
      },
      "createdTime": "2019-07-16T18:23:21.000Z"
    }
]}

AIRTABLE_GREGOR_SAMPLE_RECORDS = {
  "records": [
    {
      "id": "rec2B6OGmQpAkQW3s",
      "fields": {
        "SeqrCollaboratorSampleID": "VCGS_FAM203_621_D1",
        "CollaboratorSampleID": "NA19675_1",
        'CollaboratorParticipantID': 'NA19675',
        'SMID': 'SM-AGHT',
        'Recontactable': 'Yes',
      },
    },
    {
      "id": "rec2B67GmXpAkQW8z",
      "fields": {
        'SeqrCollaboratorSampleID': 'NA19679',
        'CollaboratorSampleID': 'NA19679',
        'CollaboratorParticipantID': 'NA19679',
        'SMID': 'SM-N1P91',
        'Recontactable': 'Yes',
      },
    },
    {
      "id": "rec2Nkg10N1KssPc3",
      "fields": {
        "SeqrCollaboratorSampleID": "HG00731",
        "CollaboratorSampleID": "VCGS_FAM203_621_D2",
        'CollaboratorParticipantID': 'VCGS_FAM203_621',
        'SMID': 'SM-JDBTM',
      },
    },
    {
      "id": "rec2Nkg1fKssJc7",
      "fields": {
        'SeqrCollaboratorSampleID': 'NA20888',
        'CollaboratorSampleID': 'NA20888',
        'CollaboratorParticipantID': 'NA20888',
        'SMID': 'SM-L5QMP',
        'Recontactable': 'No',
      },
    },
]}

AIRTABLE_GREGOR_RECORDS = {
  "records": [
    {
      "id": "rec2B6OGmQpAkQW3s",
      "fields": {
        'CollaboratorParticipantID': 'VCGS_FAM203_621',
        'CollaboratorSampleID_wes': 'VCGS_FAM203_621_D2',
        'SMID_wes': 'SM-JDBTM',
        'seq_library_prep_kit_method_wes': 'Kapa HyperPrep',
        'read_length_wes': '151',
        'experiment_type_wes': 'exome',
        'targeted_regions_method_wes': 'Twist',
        'targeted_region_bed_file': 'gs://fc-eb352699-d849-483f-aefe-9d35ce2b21ac/SR_experiment.bed',
        'date_data_generation_wes': '2022-08-15',
        'target_insert_size_wes': '385',
        'sequencing_platform_wes': 'NovaSeq',
        'aligned_dna_short_read_file_wes': 'gs://fc-eb352699-d849-483f-aefe-9d35ce2b21ac/Broad_COL_FAM1_1_D1.cram',
        'aligned_dna_short_read_index_file_wes': 'gs://fc-eb352699-d849-483f-aefe-9d35ce2b21ac/Broad_COL_FAM1_1_D1.crai',
        'md5sum_wes': '129c28163df082',
        'reference_assembly': 'GRCh38',
        'alignment_software_dna': 'BWA-MEM-2.3',
        'mean_coverage_wgs': '42.4',
        'analysis_details': 'DOI:10.5281/zenodo.4469317',
        'called_variants_dna_short_read_id': 'SX2-3',
        'aligned_dna_short_read_set_id': 'BCM_H7YG5DSX2',
        'called_variants_dna_file': 'gs://fc-fed09429-e563-44a7-aaeb-776c8336ba02/COL_FAM1_1_D1.SV.vcf',
        'caller_software': 'gatk4.1.2',
        'variant_types': 'SNV',
      },
    },
    {
      "id": "rec2B6OGmCVzkQW3s",
      "fields": {
        'CollaboratorParticipantID': 'NA19675',
        'CollaboratorSampleID_wgs': 'NA19675_1',
        'SMID_wgs': 'SM-AGHT-2',
        'experiment_type_wgs': 'genome',
      },
    },
    {
      "id": "rec4B7OGmQpVkQW7z",
      "fields": {
        'CollaboratorParticipantID': 'NA19679',
        'CollaboratorSampleID_rna': 'NA19679',
        'SMID_rna': 'SM-N1P91',
        'seq_library_prep_kit_method_rna': 'Unknown',
        'library_prep_type_rna': 'stranded poly-A pulldown',
        'read_length_rna': '151',
        'experiment_type_rna': 'paired-end',
        'single_or_paired_ends_rna': 'paired-end',
        'date_data_generation_rna': '2023-02-11',
        'sequencing_platform_rna': 'NovaSeq',
        'aligned_rna_short_read_file': 'gs://fc-eb352699-d849-483f-aefe-9d35ce2b21ac/NA19679.Aligned.out.cram',
        'aligned_rna_short_read_index_file': 'gs://fc-eb352699-d849-483f-aefe-9d35ce2b21ac/NA19679.Aligned.out.crai',
        'md5sum_rna': 'f6490b8ebdf2',
        '5prime3prime_bias_rna': '1.05',
        'gene_annotation_rna': 'GENCODEv26',
        'reference_assembly': 'GRCh38',
        'reference_assembly_uri_rna': 'gs://gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.fasta',
        'alignment_software_rna': 'STARv2.7.10b',
        'alignment_log_file_rna': 'gs://fc-eb352699-d849-483f-aefe-9d35ce2b21ac/NA19679.Log.final.out',
        'percent_uniquely_aligned_rna': '80.53',
        'percent_multimapped_rna': '17.08',
        'percent_unaligned_rna': '1.71',
        'percent_mRNA': '80.2',
        'percent_rRNA': '5.9',
        'RIN_rna': '8.9818',
        'total_reads_rna': '106,842,386',
        'within_site_batch_name_rna': 'LCSET-26942',
        'estimated_library_size_rna': '19,480,858',
        'variant_types': 'SNV',
      },
    },
    {
      "id": "rec2BFCGmQpAkQ7x",
      "fields": {
        'CollaboratorParticipantID': 'NA20888',
        'CollaboratorSampleID_wes': 'NA20888',
        'CollaboratorSampleID_wgs': 'NA20888_1',
        'SMID_wes': 'SM-L5QMP',
        'SMID_wgs': 'SM-L5QMWP',
        'seq_library_prep_kit_method_wes': 'Kapa HyperPrep',
        'seq_library_prep_kit_method_wgs': 'Kapa HyperPrep w/o amplification',
        'read_length_wes': '151',
        'read_length_wgs': '200',
        'experiment_type_wes': 'exome',
        'experiment_type_wgs': 'genome',
        'targeted_regions_method_wes': 'Twist',
        'targeted_region_bed_file': 'gs://fc-eb352699-d849-483f-aefe-9d35ce2b21ac/SR_experiment.bed',
        'date_data_generation_wes': '2022-06-05',
        'date_data_generation_wgs': '2023-03-13',
        'target_insert_size_wes': '380',
        'target_insert_size_wgs': '450',
        'sequencing_platform_wes': 'NovaSeq',
        'sequencing_platform_wgs': 'NovaSeq2',
        'aligned_dna_short_read_file_wes': 'gs://fc-eb352699-d849-483f-aefe-9d35ce2b21ac/Broad_NA20888.cram',
        'aligned_dna_short_read_index_file_wes': 'gs://fc-eb352699-d849-483f-aefe-9d35ce2b21ac/Broad_NA20888.crai',
        'aligned_dna_short_read_file_wgs': 'gs://fc-eb352699-d849-483f-aefe-9d35ce2b21ac/Broad_NA20888_1.cram',
        'aligned_dna_short_read_index_file_wgs': 'gs://fc-eb352699-d849-483f-aefe-9d35ce2b21ac/Broad_NA20888_1.crai',
        'md5sum_wes': 'a6f6308866765ce8',
        'md5sum_wgs': '2aa33e8c32020b1c',
        'reference_assembly': 'GRCh38',
        'alignment_software_dna': 'BWA-MEM-2.3',
        'mean_coverage_wes': '42.8',
        'mean_coverage_wgs': '36.1',
        'analysis_details': '',
        'called_variants_dna_short_read_id': '',
        'aligned_dna_short_read_set_id': 'Broad_NA20888_D1',
        'called_variants_dna_file': '',
        'caller_software': 'NA',
        'variant_types': 'SNV',
      },
    },
]}
EXPECTED_GREGOR_FILES = [
    'participant', 'family', 'phenotype', 'analyte', 'experiment_dna_short_read',
    'aligned_dna_short_read', 'aligned_dna_short_read_set', 'called_variants_dna_short_read',
    'experiment_rna_short_read', 'aligned_rna_short_read', 'experiment', 'genetic_findings',
]

MOCK_DATA_MODEL_URL = 'http://raw.githubusercontent.com/gregor_data_model.json'
MOCK_DATA_MODEL = {
    'name': 'test data model',
    'tables': [
        {
            'table': 'participant',
            'required': True,
            'columns': [
                {'column': 'participant_id', 'required': True, 'data_type': 'string'},
                {'column': 'internal_project_id'},
                {'column': 'gregor_center', 'required': True, 'data_type': 'enumeration', 'enumerations': ['BCM', 'BROAD', 'UW']},
                {'column': 'consent_code', 'required': True, 'data_type': 'enumeration', 'enumerations': ['GRU', 'HMB']},
                {'column': 'recontactable', 'data_type': 'enumeration', 'enumerations': ['Yes', 'No']},
                {'column': 'prior_testing'},
                {'column': 'pmid_id'},
                {'column': 'family_id', 'required': True},
                {'column': 'paternal_id'},
                {'column': 'maternal_id'},
                {'column': 'twin_id'},
                {'column': 'proband_relationship'},
                {'column': 'proband_relationship_detail'},
                {'column': 'sex', 'required': True, 'data_type': 'enumeration', 'enumerations': ['Male', 'Female', 'Unknown']},
                {'column': 'sex_detail'},
                {'column': 'reported_race', 'data_type': 'enumeration', 'enumerations': ['American Indian or Alaska Native', 'Asian', 'Black or African American', 'Native Hawaiian or Other Pacific Islander', 'Middle Eastern or North African', 'White']},
                {'column': 'reported_ethnicity', 'data_type': 'enumeration', 'enumerations': ['Hispanic or Latino', 'Not Hispanic or Latino']},
                {'column': 'ancestry_detail'},
                {'column': 'age_at_last_observation'},
                {'column': 'affected_status', 'required': True, 'data_type': 'enumeration', 'enumerations': ['Affected', 'Unaffected', 'Unknown']},
                {'column': 'phenotype_description'},
                {'column': 'age_at_enrollment'},
                {'column': 'solve_status', 'required': True, 'data_type': 'enumeration', 'enumerations': ['Yes', 'Likely', 'No', 'Partial']},
                {'column': 'missing_variant_case', 'required': True, 'data_type': 'enumeration', 'enumerations': ['Yes', 'No']},
            ],
        },
        {
            'table': 'family',
            'required': True,
            'columns': [
                {'column': 'family_id', 'required': True, 'data_type': 'string'},
                {'column': 'consanguinity', 'required': True, 'data_type': 'enumeration', 'enumerations': ['None suspected', 'Suspected', 'Present', 'Unknown']},
                {'column': 'consanguinity_detail'},
            ]
        },
        {
            'table': 'phenotype',
            'required': True,
            'columns': [
                {'column': 'phenotype_id'},
                {'column': 'participant_id', 'references': '> participant.participant_id', 'required': True, 'data_type': 'string'},
                {'column': 'term_id', 'required': True},
                {'column': 'presence', 'required': True, 'data_type': 'enumeration', 'enumerations': ['Present', 'Absent', 'Unknown']},
                {'column': 'ontology', 'required': True, 'data_type': 'enumeration', 'enumerations': ['HPO', 'MONDO']},
                {'column': 'additional_details'},
                {'column': 'onset_age_range'},
                {'column': 'additional_modifiers'},
            ]
        },
        {
            'table': 'analyte',
            'required': True,
            'columns': [
                {'column': 'analyte_id', 'required': True, 'data_type': 'string'},
                {'column': 'participant_id', 'required': True, 'data_type': 'string'},
                {'column': 'analyte_type', 'data_type': 'enumeration', 'enumerations': ['DNA', 'RNA', 'cDNA', 'blood plasma', 'frozen whole blood', 'high molecular weight DNA', 'urine']},
                {'column': 'analyte_processing_details'},
                {'column': 'primary_biosample'},
                {'column': 'primary_biosample_id'},
                {'column': 'primary_biosample_details'},
                {'column': 'tissue_affected_status', 'required': True, 'data_type': 'enumeration', 'enumerations': ['Yes', 'No']},
            ]
        },
        {
            'table': 'experiment',
            'columns': [
                {'column': 'experiment_id', 'required': True, 'data_type': 'string'},
                {'column': 'table_name', 'required': True, 'data_type': 'enumeration', 'enumerations': ['experiment_dna_short_read', 'experiment_rna_short_read']},
                {'column': 'id_in_table', 'required': True},
                {'column': 'participant_id', 'required': True},
            ]
        },
        {
            'table': 'experiment_dna_short_read',
            'required': 'CONDITIONAL (aligned_dna_short_read, aligned_dna_short_read_set, called_variants_dna_short_read)',
            'columns': [
                {'column': 'experiment_dna_short_read_id', 'required': True},
                {'column': 'analyte_id', 'required': True},
                {'column': 'experiment_sample_id', 'required': True},
                {'column': 'seq_library_prep_kit_method'},
                {'column': 'read_length', 'data_type': 'integer'},
                {'column': 'experiment_type', 'required': True, 'data_type': 'enumeration', 'enumerations': ['targeted', 'genome', 'exome']},
                {'column': 'targeted_regions_method'},
                {'column': 'targeted_region_bed_file', 'data_type': 'string', 'is_bucket_path': True},
                {'column': 'date_data_generation', 'data_type': 'date'},
                {'column': 'target_insert_size', 'data_type': 'integer'},
                {'column': 'sequencing_platform'},
            ],
        },
        {
            'table': 'aligned_dna_short_read',
            'required': 'CONDITIONAL (aligned_dna_short_read_set, called_variants_dna_short_read)',
            'columns': [
                {'column': 'aligned_dna_short_read_id', 'required': True},
                {'column': 'experiment_dna_short_read_id', 'required': True},
                {'column': 'aligned_dna_short_read_file', 'is_unique': True, 'data_type': 'string', 'is_bucket_path': True},
                {'column': 'aligned_dna_short_read_index_file', 'data_type': 'string', 'is_bucket_path': True},
                {'column': 'md5sum', 'is_unique': True},
                {'column': 'reference_assembly', 'data_type': 'enumeration', 'enumerations': ['GRCh38', 'GRCh37']},
                {'column': 'reference_assembly_uri'},
                {'column': 'reference_assembly_details'},
                {'column': 'mean_coverage', 'data_type': 'float'},
                {'column': 'alignment_software', 'required': True},
                {'column': 'analysis_details', 'data_type': 'string'},
                {'column': 'quality_issues'},
            ],
        },
        {
            'table': 'aligned_dna_short_read_set',
            'required': 'CONDITIONAL (called_variants_dna_short_read)',
            'columns': [
                {'column': 'aligned_dna_short_read_set_id', 'required': True},
                {'column': 'aligned_dna_short_read_id', 'required': True},
            ],
        },
        {
            'table': 'called_variants_dna_short_read',
            'columns': [
                {'column': 'called_variants_dna_short_read_id', 'required': True, 'is_unique': True},
                {'column': 'aligned_dna_short_read_set_id', 'required': True},
                {'column': 'called_variants_dna_file', 'is_unique': True, 'data_type': 'string', 'is_bucket_path': True},
                {'column': 'md5sum', 'required': True, 'is_unique': True},
                {'column': 'caller_software', 'required': True},
                {'column': 'variant_types', 'required': True, 'data_type': 'enumeration', 'enumerations': ['SNV', 'INDEL', 'SV', 'CNV', 'RE','MEI', 'STR']},
                {'column': 'analysis_details'},
            ],
        },
        {
            'table': 'experiment_rna_short_read',
            'required': 'CONDITIONAL (aligned_rna_short_read)',
            'columns': [
                {'column': 'experiment_rna_short_read_id', 'required': True},
                {'column': 'analyte_id', 'required': True},
                {'column': 'experiment_sample_id'},
                {'column': 'seq_library_prep_kit_method'},
                {'column': 'read_length', 'data_type': 'integer'},
                {'column': 'experiment_type'},
                {'column': 'date_data_generation', 'data_type': 'date'},
                {'column': 'sequencing_platform'},
                {'column': 'library_prep_type'},
                {'column': 'single_or_paired_ends'},
                {'column': 'within_site_batch_name'},
                {'column': 'RIN', 'data_type': 'float'},
                {'column': 'estimated_library_size', 'data_type': 'float'},
                {'column': 'total_reads', 'data_type': 'integer'},
                {'column': 'percent_rRNA', 'data_type': 'float'},
                {'column': 'percent_mRNA', 'data_type': 'float'},
                {'column': '5prime3prime_bias', 'data_type': 'float'},
                {'column': 'percent_mtRNA', 'data_type': 'float'},
                {'column': 'percent_Globin', 'data_type': 'float'},
                {'column': 'percent_UMI', 'data_type': 'float'},
                {'column': 'percent_GC', 'data_type': 'float'},
                {'column': 'percent_chrX_Y', 'data_type': 'float'},
            ],
        },
        {
            'table': 'aligned_rna_short_read',
            'columns': [
                {'column': 'aligned_rna_short_read_id', 'required': True},
                {'column': 'experiment_rna_short_read_id', 'required': True},
                {'column': 'aligned_rna_short_read_file', 'is_unique': True, 'data_type': 'string', 'is_bucket_path': True},
                {'column': 'aligned_rna_short_read_index_file', 'data_type': 'string', 'is_bucket_path': True},
                {'column': 'md5sum', 'is_unique': True},
                {'column': 'reference_assembly', 'data_type': 'enumeration', 'enumerations': ['GRCh38', 'GRCh37']},
                {'column': 'reference_assembly_uri'},
                {'column': 'reference_assembly_details'},
                {'column': 'mean_coverage', 'data_type': 'float'},
                {'column': 'gene_annotation', 'required': True},
                {'column': 'gene_annotation_details'},
                {'column': 'alignment_software', 'required': True},
                {'column': 'alignment_log_file', 'required': True},
                {'column': 'alignment_postprocessing'},
                {'column': 'percent_uniquely_aligned'},
                {'column': 'percent_multimapped'},
                {'column': 'percent_unaligned'},
                {'column': 'quality_issues'},
            ],
        },
        {
            'table': 'genetic_findings',
            'columns': [
                {'column': 'genetic_findings_id', 'required': True},
                {'column': 'participant_id', 'required': True},
                {'column': 'experiment_id'},
                {'column': 'variant_type', 'required': True, 'data_type': 'enumeration', 'enumerations': ['SNV/INDEL', 'SV', 'CNV', 'RE', 'MEI']},
                {'column': 'variant_reference_assembly', 'required': True, 'data_type': 'enumeration', 'enumerations': ['GRCh37', 'GRCh38']},
                {'column': 'chrom', 'required': True},
                {'column': 'pos', 'required': True, 'data_type': 'integer'},
                {'column': 'ref','required': True},
                {'column': 'alt', 'required': True},
                {'column': 'ClinGen_allele_ID'},
                {'column': 'gene', 'required': True},
                {'column': 'transcript'},
                {'column': 'hgvsc'},
                {'column': 'hgvsp'},
                {'column': 'zygosity', 'required': True, 'data_type': 'enumeration', 'enumerations': ['Heterozygous', 'Homozygous', 'Hemizygous', 'Heteroplasmy', 'Homoplasmy', 'Mosaic']},
                {'column': 'allele_balance_or_heteroplasmy_percentage', 'data_type': 'float'},
                {'column': 'variant_inheritance', 'data_type': 'enumeration', 'enumerations': ['de novo', 'maternal', 'paternal', 'biparental', 'nonmaternal', 'nonpaternal', 'unknown']},
                {'column': 'linked_variant'},
                {'column': 'linked_variant_phase'},
                {'column': 'gene_known_for_phenotype', 'required': True, 'data_type': 'enumeration', 'enumerations': ['Known', 'Candidate']},
                {'column': 'known_condition_name'},
                {'column': 'condition_id'},
                {'column': 'condition_inheritance', 'data_type': 'enumeration', 'multi_value_delimiter': '|', 'enumerations': ['Autosomal recessive', 'Autosomal dominant', 'X-linked', 'Mitochondrial', 'Y-linked', 'Contiguous gene syndrome', 'Somatic mosaicism', 'Digenic', 'Other', 'Unknown']},
                {'column': 'phenotype_contribution', 'data_type': 'enumeration', 'enumerations': ['Partial', 'Full', 'Uncertain']},
                {'column': 'partial_contribution_explained'},
                {'column': 'additional_family_members_with_variant'},
                {'column': 'method_of_discovery', 'data_type': 'enumeration', 'multi_value_delimiter': '|', 'enumerations': ['SR-ES', 'SR-GS', 'LR-GS', 'SNP array']},
                {'column': 'notes'}
            ]
        },
    ]
}
MOCK_DATA_MODEL_RESPONSE = json.dumps(MOCK_DATA_MODEL, indent=2).replace('"references"', '//"references"')

INVALID_MODEL_TABLES = {
    'participant': {
        'internal_project_id': {'data_type': 'reference'},
        'prior_testing': {'data_type': 'enumeration'},
        'proband_relationship': {'required': True},
        'reported_race': {'enumerations': ['Asian', 'White', 'Black']},
        'age_at_enrollment': {'data_type': 'date'}
    },
    'aligned_dna_short_read': {
        'analysis_details': {'is_bucket_path': True},
        'reference_assembly': {'data_type': 'integer'},
        'mean_coverage': {'required': True},
        'alignment_software': {'is_unique': True},
    },
    'aligned_dna_short_read_set': {},
    'experiment_rna_short_read': {'date_data_generation': {'data_type': 'float'}},
    'genetic_findings': {'experiment_id': {'required': True}},
}
INVALID_TABLES = [
    {**t, 'columns': [{**c, **(INVALID_MODEL_TABLES[t['table']].get(c['column'], {}))} for c in t['columns']]}
    for t in MOCK_DATA_MODEL['tables'] if t['table'] in INVALID_MODEL_TABLES
]
INVALID_TABLES[0]['columns'] = [c for c in INVALID_TABLES[0]['columns'] if c['column'] not in {
    'pmid_id', 'age_at_last_observation', 'ancestry_detail', 'missing_variant_case',
}]
MOCK_INVALID_DATA_MODEL = {
    'tables': [
        {
            'table': 'subject',
            'required': True,
            'columns': [{'column': 'subject_id', 'required': True}],
        },
        {
            'table': 'dna_read_data',
            'columns': [{'column': 'analyte_id', 'required': True}],
        },
        {
            'table': 'dna_read_data_set',
            'required': 'CONDITIONAL (aligned_dna_short_read_set, dna_read_data)',
            'columns': [{'column': 'analyte_id', 'required': True}],
        },
    ] + INVALID_TABLES
}


class ReportAPITest(AirtableTest):

    def _get_zip_files(self, mock_zip, filenames):
        mock_write_zip = mock_zip.return_value.__enter__.return_value.writestr
        self.assertEqual(mock_write_zip.call_count, len(filenames))
        mock_write_zip.assert_has_calls([mock.call(file, mock.ANY) for file in filenames])

        return (
            [row.split('\t') for row in mock_write_zip.call_args_list[i][0][1].split('\n') if row]
            for i in range(len(filenames))
        )

    def test_seqr_stats(self):
        no_access_project = Project.objects.get(id=2)
        no_access_project.workspace_namespace = None
        no_access_project.save()

        url = reverse(seqr_stats)
        self.check_analyst_login(url)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertSetEqual(set(response_json.keys()), {'projectsCount', 'individualsCount', 'familiesCount', 'sampleCountsByType'})
        self.assertDictEqual(response_json['projectsCount'], self.STATS_DATA['projectsCount'])
        self.assertDictEqual(response_json['individualsCount'], self.STATS_DATA['individualsCount'])
        self.assertDictEqual(response_json['familiesCount'], self.STATS_DATA['familiesCount'])
        self.assertDictEqual(response_json['sampleCountsByType'], self.STATS_DATA['sampleCountsByType'])

        self.check_no_analyst_no_access(url)

    def test_get_category_projects(self):
        url = reverse(get_category_projects, args=['GREGoR'])
        self.check_analyst_login(url)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertListEqual(list(response_json.keys()), ['projectGuids'])
        self.assertSetEqual(set(response_json['projectGuids']), {PROJECT_GUID, COMPOUND_HET_PROJECT_GUID})

        self.check_no_analyst_no_access(url)

    @mock.patch('seqr.views.apis.report_api.timezone')
    def test_discovery_sheet(self, mock_timezone):
        non_project_url = reverse(discovery_sheet, args=[NON_PROJECT_GUID])
        self.check_analyst_login(non_project_url)

        mock_timezone.now.return_value = pytz.timezone("US/Eastern").localize(parse_datetime("2020-04-27 20:16:01"), is_dst=None)
        response = self.client.get(non_project_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason_phrase, 'Invalid project {}'.format(NON_PROJECT_GUID))
        response_json = response.json()
        self.assertEqual(response_json['error'], 'Invalid project {}'.format(NON_PROJECT_GUID))

        unauthorized_project_url = reverse(discovery_sheet, args=[NO_ANALYST_PROJECT_GUID])
        response = self.client.get(unauthorized_project_url)
        self.assertEqual(response.status_code, 403)

        empty_project_url = reverse(discovery_sheet, args=[PROJECT_EMPTY_GUID])

        response = self.client.get(empty_project_url)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertSetEqual(set(response_json.keys()), {'rows', 'errors'})
        self.assertListEqual(response_json['rows'], [])
        self.assertListEqual(response_json['errors'], ["No data loaded for project: Empty Project"])

        url = reverse(discovery_sheet, args=[PROJECT_GUID])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertSetEqual(set(response_json.keys()), {'rows', 'errors'})
        self.assertListEqual(response_json['errors'], ['No data loaded for family: 9. Skipping...', 'No data loaded for family: no_individuals. Skipping...'])
        self.assertEqual(len(response_json['rows']), 10)
        self.assertIn(EXPECTED_DISCOVERY_SHEET_ROW, response_json['rows'])

        # test compound het reporting
        url = reverse(discovery_sheet, args=[COMPOUND_HET_PROJECT_GUID])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertSetEqual(set(response_json.keys()), {'rows', 'errors'})
        self.assertListEqual(response_json['errors'], [
            'HPO category field not set for some HPO terms in 11', 'HPO category field not set for some HPO terms in 12',
        ])
        self.assertEqual(len(response_json['rows']), 2)
        self.assertIn(EXPECTED_DISCOVERY_SHEET_COMPOUND_HET_ROW, response_json['rows'])

        self.check_no_analyst_no_access(url)

    # @mock.patch('seqr.views.utils.export_utils.zipfile.ZipFile')
    # @mock.patch('seqr.views.utils.airtable_utils.is_google_authenticated')
    # @responses.activate
    # def test_anvil_export(self, mock_google_authenticated,  mock_zip):
    #     mock_google_authenticated.return_value = False
    #     url = reverse(anvil_export, args=[PROJECT_GUID])
    #     self.check_analyst_login(url)
    #
    #     unauthorized_project_url = reverse(anvil_export, args=[NO_ANALYST_PROJECT_GUID])
    #     response = self.client.get(unauthorized_project_url)
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(response.json()['error'], 'Permission Denied')
    #
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(response.json()['error'], 'Permission Denied')
    #     mock_google_authenticated.return_value = True
    #
    #     responses.add(responses.GET, '{}/app3Y97xtbbaOopVR/Samples'.format(AIRTABLE_URL), json=AIRTABLE_SAMPLE_RECORDS, status=200)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(
    #         response.get('content-disposition'),
    #         'attachment; filename="1kg project nme with unide_AnVIL_Metadata.zip"'
    #     )
    #
    #     subject_file, sample_file, family_file, discovery_file = self._get_zip_files(mock_zip, [
    #         '1kg project n\xe5me with uni\xe7\xf8de_PI_Subject.tsv',
    #         '1kg project n\xe5me with uni\xe7\xf8de_PI_Sample.tsv',
    #         '1kg project n\xe5me with uni\xe7\xf8de_PI_Family.tsv',
    #         '1kg project n\xe5me with uni\xe7\xf8de_PI_Discovery.tsv',
    #     ])
    #
    #     self.assertEqual(subject_file[0], [
    #         'entity:subject_id', '01-subject_id', '02-prior_testing', '03-project_id', '04-pmid_id',
    #         '05-dbgap_study_id', '06-dbgap_subject_id', '07-multiple_datasets',
    #         '08-family_id', '09-paternal_id', '10-maternal_id', '11-twin_id', '12-proband_relationship', '13-sex',
    #         '14-ancestry', '15-ancestry_detail', '16-age_at_last_observation', '17-phenotype_group', '18-disease_id',
    #         '19-disease_description', '20-affected_status', '21-congenital_status', '22-age_of_onset', '23-hpo_present',
    #         '24-hpo_absent', '25-phenotype_description', '26-solve_state'])
    #     self.assertIn([
    #         'NA19675_1', 'NA19675_1', '-', u'1kg project nme with unide', '34415322', 'dbgap_stady_id_1',
    #         'dbgap_subject_id_1', 'No', '1', 'NA19678', 'NA19679', '-', 'Self', 'Male', 'Other', 'Middle Eastern', '-',
    #         '-', 'OMIM:615120;OMIM:615123', 'Myasthenic syndrome; congenital; 8; with pre- and postsynaptic defects;',
    #         'Affected', 'Adult onset', '-', 'HP:0001631|HP:0002011|HP:0001636', 'HP:0011675|HP:0001674|HP:0001508',
    #         'myopathy', 'Tier 1'], subject_file)
    #
    #     self.assertEqual(sample_file[0], [
    #         'entity:sample_id', '01-subject_id', '02-sample_id', '03-dbgap_sample_id', '04-sequencing_center',
    #         '05-sample_source', '06-tissue_affected_status',])
    #     self.assertIn(
    #         ['NA19675_1', 'NA19675_1', 'NA19675', 'SM-A4GQ4', 'Broad', '-', '-'],
    #         sample_file,
    #     )
    #
    #     self.assertEqual(family_file[0], [
    #         'entity:family_id', '01-family_id', '02-consanguinity', '03-consanguinity_detail', '04-pedigree_image',
    #         '05-pedigree_detail', '06-family_history', '07-family_onset'])
    #     self.assertIn([
    #         '1', '1', 'Present', '-', '-', '-', '-', '-',
    #     ], family_file)
    #
    #     self.assertEqual(len(discovery_file), 6)
    #     self.assertEqual(discovery_file[0], [
    #         'entity:discovery_id', '01-subject_id', '02-sample_id', '03-Gene', '04-Gene_Class',
    #         '05-inheritance_description', '06-Zygosity', '07-variant_genome_build', '08-Chrom', '09-Pos',
    #         '10-Ref', '11-Alt', '12-hgvsc', '13-hgvsp', '14-Transcript', '15-sv_name', '16-sv_type',
    #         '17-significance', '18-discovery_notes'])
    #     self.assertIn([
    #         'HG00731', 'HG00731', 'HG00731', 'RP11', 'Known', 'Autosomal recessive (homozygous)',
    #         'Homozygous', 'GRCh37', '1', '248367227', 'TC', 'T', '-', '-', '-', '-', '-', '-', '-'], discovery_file)
    #     self.assertIn([
    #         'NA19675_1', 'NA19675_1', 'NA19675', 'RP11', 'Tier 1 - Candidate', 'de novo',
    #         'Heterozygous', 'GRCh37', '21', '3343353', 'GAGA', 'G', 'c.375_377delTCT', 'p.Leu126del', 'ENST00000258436',
    #         '-', '-', '-', '-'], discovery_file)
    #     self.assertIn([
    #         'HG00733', 'HG00733', 'HG00733', 'OR4G11P', 'Known', 'Unknown / Other', 'Heterozygous', 'GRCh38.p12', '19',
    #         '1912633', 'G', 'T', '-', '-', 'ENST00000371839', '-', '-', '-',
    #         'The following variants are part of the multinucleotide variant 19-1912632-GC-TT '
    #         '(c.586_587delinsTT, p.Ala196Leu): 19-1912633-G-T, 19-1912634-C-T'],
    #         discovery_file)
    #     self.assertIn([
    #         'HG00733', 'HG00733', 'HG00733', 'OR4G11P', 'Known', 'Unknown / Other', 'Heterozygous', 'GRCh38.p12', '19',
    #         '1912634', 'C', 'T', '-', '-', 'ENST00000371839', '-', '-', '-',
    #         'The following variants are part of the multinucleotide variant 19-1912632-GC-TT (c.586_587delinsTT, '
    #         'p.Ala196Leu): 19-1912633-G-T, 19-1912634-C-T'],
    #         discovery_file)
    #
    #     self.check_no_analyst_no_access(url)
    #
    #     # Test non-broad analysts do not have access
    #     self.login_pm_user()
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(response.json()['error'], 'Permission Denied')
    #
    # @mock.patch('seqr.views.utils.airtable_utils.MAX_OR_FILTERS', 4)
    # @mock.patch('seqr.views.utils.airtable_utils.AIRTABLE_API_KEY', 'mock_key')
    # @mock.patch('seqr.views.utils.airtable_utils.is_google_authenticated')
    # @responses.activate
    # def test_sample_metadata_export(self, mock_google_authenticated):
    #     mock_google_authenticated.return_value = False
    #     url = reverse(sample_metadata_export, args=[COMPOUND_HET_PROJECT_GUID])
    #     self.check_analyst_login(url)
    #
    #     unauthorized_project_url = reverse(sample_metadata_export, args=[NO_ANALYST_PROJECT_GUID])
    #     response = self.client.get(unauthorized_project_url)
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(response.json()['error'], 'Permission Denied')
    #
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual( response.json()['error'], 'Permission Denied')
    #     mock_google_authenticated.return_value = True
    #
    #     # Test invalid airtable responses
    #     responses.add(responses.GET, '{}/app3Y97xtbbaOopVR/Samples'.format(AIRTABLE_URL), status=402)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 402)
    #
    #     responses.reset()
    #     responses.add(responses.GET, '{}/app3Y97xtbbaOopVR/Samples'.format(AIRTABLE_URL), status=200)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 500)
    #     self.assertIn(response.json()['error'], ['Unable to retrieve airtable data: No JSON object could be decoded',
    #                                     'Unable to retrieve airtable data: Expecting value: line 1 column 1 (char 0)'])
    #
    #     responses.reset()
    #     responses.add(responses.GET, '{}/app3Y97xtbbaOopVR/Samples'.format(AIRTABLE_URL),
    #                   json=PAGINATED_AIRTABLE_SAMPLE_RECORDS, status=200)
    #     responses.add(responses.GET, '{}/app3Y97xtbbaOopVR/Samples'.format(AIRTABLE_URL),
    #                   json=AIRTABLE_SAMPLE_RECORDS, status=200)
    #     responses.add(responses.GET, '{}/app3Y97xtbbaOopVR/Collaborator'.format(AIRTABLE_URL),
    #                   json=AIRTABLE_COLLABORATOR_RECORDS, status=200)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 500)
    #     self.assertEqual(
    #         response.json()['error'],
    #         'Found multiple airtable records for sample NA19675 with mismatched values in field dbgap_study_id')
    #     self.assertEqual(len(responses.calls), 3)
    #     first_formula = "OR({CollaboratorSampleID}='NA20885',{CollaboratorSampleID}='NA20888',{CollaboratorSampleID}='NA20889'," \
    #                     "{SeqrCollaboratorSampleID}='NA20885')"
    #     expected_params = {
    #         'fields[]': mock.ANY,
    #         'filterByFormula': first_formula,
    #     }
    #     expected_fields = [
    #         'SeqrCollaboratorSampleID', 'CollaboratorSampleID', 'Collaborator', 'dbgap_study_id', 'dbgap_subject_id',
    #         'dbgap_sample_id', 'SequencingProduct', 'dbgap_submission',
    #     ]
    #     self.assertDictEqual(responses.calls[0].request.params, expected_params)
    #     self.assertListEqual(_get_list_param(responses.calls[0].request, 'fields%5B%5D'), expected_fields)
    #     expected_offset_params = {'offset': 'abc123'}
    #     expected_offset_params.update(expected_params)
    #     self.assertDictEqual(responses.calls[1].request.params, expected_offset_params)
    #     self.assertListEqual(_get_list_param(responses.calls[1].request, 'fields%5B%5D'), expected_fields)
    #     expected_params['filterByFormula'] = "OR({SeqrCollaboratorSampleID}='NA20888',{SeqrCollaboratorSampleID}='NA20889')"
    #     self.assertDictEqual(responses.calls[2].request.params, expected_params)
    #     self.assertListEqual(_get_list_param(responses.calls[2].request, 'fields%5B%5D'), expected_fields)
    #
    #     # Test success
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     response_json = response.json()
    #     self.assertListEqual(list(response_json.keys()), ['rows'])
    #     self.assertIn(EXPECTED_SAMPLE_METADATA_ROW, response_json['rows'])
    #     self.assertEqual(len(responses.calls), 6)
    #     self.assertDictEqual(responses.calls[-1].request.params, {
    #         'fields[]': 'CollaboratorID',
    #         'filterByFormula': "OR(RECORD_ID()='recW24C2CJW5lT64K',RECORD_ID()='reca4hcBnbA2cnZf9')",
    #     })
    #     self.assertSetEqual({call.request.headers['Authorization'] for call in responses.calls}, {'Bearer mock_key'})
    #
    #     # Test empty project
    #     empty_project_url = reverse(sample_metadata_export, args=[PROJECT_EMPTY_GUID])
    #     response = self.client.get(empty_project_url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertDictEqual(response.json(), {'rows': []})
    #
    #     self.check_no_analyst_no_access(url)
    #
    #     # Test non-broad analysts do not have access
    #     self.login_pm_user()
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(response.json()['error'], 'Permission Denied')
    #
    # @mock.patch('seqr.views.apis.report_api.datetime')
    # @mock.patch('seqr.views.utils.export_utils.zipfile.ZipFile')
    # @responses.activate
    # def test_gregor_export(self, mock_zip, mock_datetime):
    #     mock_datetime.now.return_value.year = 2020
    #
    #     url = reverse(gregor_export, args=['HMB'])
    #     self.check_analyst_login(url)
    #
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(
    #         response.get('content-disposition'),
    #         'attachment; filename="GREGoR Reports HMB.zip"'
    #     )
    #
    #     files = self._get_zip_files(mock_zip, [
    #         'participant.tsv', 'family.tsv', 'phenotype.tsv', 'analyte.tsv', 'experiment_dna_short_read.tsv',
    #         'aligned_dna_short_read.tsv', 'aligned_dna_short_read_set.tsv', 'called_variants_dna_short_read.tsv',
    #     ])
    #     participant_file, family_file, phenotype_file, analyte_file, experiment_file, read_file, read_set_file, called_file = files
    #
    #     self.assertEqual(len(participant_file), 14)
    #     self.assertEqual(participant_file[0], [
    #         'participant_id', 'internal_project_id', 'gregor_center', 'consent_code', 'recontactable', 'prior_testing',
    #         'pmid_id', 'family_id', 'paternal_id', 'maternal_id', 'twin_id', 'proband_relationship',
    #         'proband_relationship_detail', 'sex', 'sex_detail', 'reported_race', 'reported_ethnicity', 'ancestry_detail',
    #         'age_at_last_observation', 'affected_status', 'phenotype_description', 'age_at_enrollment',
    #     ])
    #     self.assertIn([
    #         'Broad_NA19675_1', 'Broad_1kg project nme with unide', 'Broad', 'HMB', '', 'IKBKAP|CCDC102B',
    #         '34415322|33665635', 'Broad_1', 'Broad_NA19678', 'Broad_NA19679', '', 'Self', '', 'Male', '',
    #         'Middle Eastern or North African', 'Unknown', '', '21', 'Affected', 'myopathy', '18',
    #     ], participant_file)
    #
    #     self.assertEqual(len(family_file), 10)
    #     self.assertEqual(family_file[0], [
    #         'family_id', 'consanguinity', 'consanguinity_detail', 'pedigree_file', 'pedigree_file_detail',
    #         'family_history_detail',
    #     ])
    #     self.assertIn(['Broad_1', 'Present', '', '', '', ''], family_file)
    #
    #     self.assertEqual(len(phenotype_file), 10)
    #     self.assertEqual(phenotype_file[0], [
    #         'phenotype_id', 'participant_id', 'term_id', 'presence', 'ontology', 'additional_details',
    #         'onset_age_range', 'additional_modifiers',
    #     ])
    #     self.assertIn([
    #         '', 'Broad_NA19675_1', 'HP:0002011', 'Present', 'HPO', '', 'HP:0003593', 'HP:0012825|HP:0003680',
    #     ], phenotype_file)
    #     self.assertIn([
    #         '', 'Broad_NA19675_1', 'HP:0001674', 'Absent', 'HPO', 'originally indicated', '', '',
    #     ], phenotype_file)
    #
    #     self.assertEqual(len(analyte_file), 14)
    #     self.assertEqual(analyte_file[0], [
    #         'analyte_id', 'participant_id', 'analyte_type', 'analyte_processing_details', 'primary_biosample',
    #         'primary_biosample_id', 'primary_biosample_details', 'tissue_affected_status', 'age_at_collection',
    #         'participant_drugs_intake', 'participant_special_diet', 'hours_since_last_meal', 'passage_number',
    #         'time_to_freeze', 'sample_transformation_detail',
    #     ])
    #     self.assertIn(
    #         ['Broad_NA19675_1', 'Broad_NA19675_1', 'DNA', '', 'UBERON:0003714', '', '', 'No', '', '', '', '', '', '', ''],
    #         analyte_file)
    #
    #     self.assertEqual(len(experiment_file), 1)
    #     self.assertEqual(experiment_file[0], [
    #         'experiment_dna_short_read_id', 'analyte_id', 'experiment_sample_id', 'seq_library_prep_kit_method',
    #         'read_length', 'experiment_type', 'targeted_regions_method', 'targeted_region_bed_file',
    #         'date_data_generation', 'target_insert_size', 'sequencing_platform',
    #     ])
    #
    #     self.assertEqual(len(experiment_file), 1)
    #     self.assertEqual(read_file[0], [
    #         'aligned_dna_short_read_id', 'experiment_dna_short_read_id', 'aligned_dna_short_read_file',
    #         'aligned_dna_short_read_index_file', 'md5sum', 'reference_assembly', 'alignment_software', 'mean_coverage',
    #         'analysis_details',
    #     ])
    #
    #     self.assertEqual(len(experiment_file), 1)
    #     self.assertEqual(read_set_file[0], ['aligned_dna_short_read_set_id', 'aligned_dna_short_read_id'])
    #
    #     self.assertEqual(len(experiment_file), 1)
    #     self.assertEqual(called_file[0], [
    #         'called_variants_dna_short_read_id', 'aligned_dna_short_read_set_id', 'called_variants_dna_file', 'md5sum',
    #         'caller_software', 'variant_types', 'analysis_details',
    #     ])
    #
    #     self.check_no_analyst_no_access(url)


class LocalReportAPITest(AuthenticationTestCase, ReportAPITest):
    fixtures = ['users', '1kg_project', 'reference_data', 'report_variants']
    STATS_DATA = {
        'projectsCount': {'non_demo': 3, 'demo': 1},
        'familiesCount': {'non_demo': 12, 'demo': 2},
        'individualsCount': {'non_demo': 16, 'demo': 4},
        'sampleCountsByType': {
            'WES__SNV_INDEL': {'demo': 1, 'non_demo': 7},
            'WGS__MITO': {'non_demo': 1},
            'WES__SV': {'non_demo': 3},
            'WGS__SV': {'non_demo': 1},
            'RNA__SNV_INDEL': {'non_demo': 3},
        },
    }


# class AnvilReportAPITest(AnvilAuthenticationTestCase, ReportAPITest):
#     fixtures = ['users', 'social_auth', '1kg_project', 'reference_data', 'report_variants']
#     ADDITIONAL_SAMPLES = []
#     STATS_DATA = {
#         'projectsCount': {'internal': 1, 'external': 1, 'no_anvil': 1, 'demo': 1},
#         'familiesCount': {'internal': 11, 'external': 1, 'no_anvil': 0, 'demo': 2},
#         'individualsCount': {'internal': 14, 'external': 2, 'no_anvil': 0, 'demo': 4},
#         'sampleCountsByType': {
#             'WES__VARIANTS': {'internal': 7, 'demo': 1},
#             'WGS__MITO': {'internal': 1},
#             'WES__SV': {'internal': 3},
#             'WGS__SV': {'external': 1},
#             'RNA__VARIANTS': {'internal': 3},
#         },
#     }
