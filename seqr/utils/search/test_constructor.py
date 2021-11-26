import json
import os
from typing import Dict, Optional

import django
from django.test import TestCase

from .expression import Expression

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from ...models import Sample, Family
from .backend import Backend
from .models import SearchModel, DatasetType
from .constructor import QueryConstructor, get_samples_by_family_index


class TestBackend(Backend):
    def search(self, expression: Expression):
        raise NotImplementedError

    def get_genome_version_for_index_name(self, index_name: str) -> Optional[DatasetType]:
        return DatasetType.VARIANT_CALLS

    def get_dataset_type_for_index_name(self, index_name: str) -> Optional[str]:
        return ''

    def get_field_metadata_for_index_name(self, index_name: str) -> Dict[str, str]:
        return {}


class TestPathogenicity(TestCase):
    def test_pathogenic(self):
        family_ids = ["F000001_trio"]

        search_model = SearchModel.from_dict(
            {"pathogenicity": {"clinvar": ["pathogenic", "likely_pathogenic"]}}
        )
        constructor = QueryConstructor(backend=TestBackend())
        expression = constructor.build_expression_from(
            search_model,
            samples_by_family_index=get_samples_by_family_index(families=family_ids),
            indices=["na12878-trio"],
        )

        print(expression.to_python())
        # SELECT * FROM variants WHERE (clinvar_clinical_significance in ("Likely_pathogenic", "Pathogenic", "Pathogenic/Likely_pathogenic"))
        print(expression.output_sql("variants"))

        s = expression.output_protobuf(fields=[], arrow_urls=[])
        self.assertEqual(
            """\
filter_expression {
 call {
  function_name: "is_in"
  arguments {
   column: "clinvar_clinical_significance"
  }
  set_lookup_options {
   values: "Likely_pathogenic"
   values: "Pathogenic"
   values: "Pathogenic/Likely_pathogenic"
  }
 }
}

max_rows: 10000""",
            s.strip(),
        )

        es = expression.output_elasticsearch(
            sort=["xpos", "variantId"], from_=0, size=100, source=[]
        )
        print(json.dumps(es))
        expected = {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "clinvar_clinical_significance": [
                                "Likely_pathogenic",
                                "Pathogenic",
                                "Pathogenic/Likely_pathogenic",
                            ]
                        }
                    }
                ]
            }
        }

        self.assertDictEqual(expected, es["query"])

    def test_2(self):
        search_model_dict = {
            "pathogenicity": {"clinvar": ["pathogenic", "likely_pathogenic"]},
            "inheritance": {
                "mode": "homozygous_recessive",
                "filter": {"A": "alt_alt", "N": "has_ref"},
                "annotationSecondary": False,
            },
            "annotations": {
                "nonsense": ["stop_gained"],
                "essential_splice_site": [
                    "splice_donor_variant",
                    "splice_acceptor_variant",
                ],
                "frameshift": ["frameshift_variant"],
                "structural": ["DEL", "DUP", "BND", "CNV", "CPX", "CTX", "INS", "INV"],
                "missense": [
                    "stop_lost",
                    "initiator_codon_variant",
                    "start_lost",
                    "protein_altering_variant",
                    "missense_variant",
                ],
                "in_frame": ["inframe_insertion", "inframe_deletion"],
            },
        }

        # families = Famhttps://www.npmjs.com/package/fast-sort#benchmarkily.objects.filter(guid__in=['F000001_trio'])
        family_ids = ["F000001_trio"]

        search_model = SearchModel.from_dict(search_model_dict)

        constructor = QueryConstructor(backend=TestBackend())
        expression = constructor.build_expression_from(
            search_model,
            samples_by_family_index=get_samples_by_family_index(families=family_ids),
            indices=["na12878-trio"],
        )

        print(expression.to_python())

        # Expected: SELECT * FROM variants WHERE ((transcriptConsequenceTerms in ("BND", "CNV", "CPX", "CTX", "DEL", "DUP", "INS", "INV", "frameshift_variant", "inframe_deletion", "inframe_insertion", "initiator_codon_variant", "missense_variant", "protein_altering_variant", "splice_acceptor_variant", "splice_donor_variant", "start_lost", "stop_gained", "stop_lost") OR clinvar_clinical_significance in ("Likely_pathogenic", "Pathogenic", "Pathogenic/Likely_pathogenic")) AND (((samples_num_alt_2 = "NA12878") AND NOT (samples_no_call = "NA12891" OR samples_num_alt_2 = "NA12891"))))
        expr = expression.output_sql("variants")
        print(expr)

        # protobuf = expression.output_protobuf(fields=[], arrow_urls=[])
        # print(protobuf)

        es = expression.output_elasticsearch([], 0, 1000, source=["xpos", "variantId"])
        es_query_expected = {
            "bool": {
                "must": [
                    {
                        "should": [
                            {
                                "terms": {
                                    "transcriptConsequenceTerms": [
                                        "BND",
                                        "CNV",
                                        "CPX",
                                        "CTX",
                                        "DEL",
                                        "DUP",
                                        "INS",
                                        "INV",
                                        "frameshift_variant",
                                        "inframe_deletion",
                                        "inframe_insertion",
                                        "initiator_codon_variant",
                                        "missense_variant",
                                        "protein_altering_variant",
                                        "splice_acceptor_variant",
                                        "splice_donor_variant",
                                        "start_lost",
                                        "stop_gained",
                                        "stop_lost",
                                    ]
                                }
                            },
                            {
                                "terms": {
                                    "clinvar_clinical_significance": [
                                        "Likely_pathogenic",
                                        "Pathogenic",
                                        "Pathogenic/Likely_pathogenic",
                                    ]
                                }
                            },
                        ],
                        "minimum_should_match": 1,
                    },
                    {
                        "must": [
                            {
                                "must": [
                                    {
                                        "should": [
                                            {"term": {"samples_num_alt_2": "NA12878"}}
                                        ],
                                        "minimum_should_match": 1,
                                    },
                                    {
                                        "negate": {
                                            "should": [
                                                {
                                                    "term": {
                                                        "samples_no_call": "NA12891"
                                                    }
                                                },
                                                {
                                                    "term": {
                                                        "samples_num_alt_2": "NA12891"
                                                    }
                                                },
                                            ],
                                            "minimum_should_match": 1,
                                        }
                                    },
                                ]
                            }
                        ]
                    },
                ]
            }
        }
        self.assertDictEqual(es_query_expected, es["query"])

        es_actual = {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "bool": {
                                "should": [
                                    {
                                        "terms": {
                                            "transcriptConsequenceTerms": [
                                                "BND",
                                                "CNV",
                                                "CPX",
                                                "CTX",
                                                "DEL",
                                                "DUP",
                                                "INS",
                                                "INV",
                                                "frameshift_variant",
                                                "inframe_deletion",
                                                "inframe_insertion",
                                                "initiator_codon_variant",
                                                "missense_variant",
                                                "protein_altering_variant",
                                                "splice_acceptor_variant",
                                                "splice_donor_variant",
                                                "start_lost",
                                                "stop_gained",
                                                "stop_lost",
                                            ]
                                        }
                                    },
                                    {
                                        "terms": {
                                            "clinvar_clinical_significance": [
                                                "Likely_pathogenic",
                                                "Pathogenic",
                                                "Pathogenic/Likely_pathogenic",
                                            ]
                                        }
                                    },
                                ]
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "must_not": [
                                                {
                                                    "term": {
                                                        "samples_no_call": "NA12891"
                                                    }
                                                },
                                                {
                                                    "term": {
                                                        "samples_num_alt_2": "NA12891"
                                                    }
                                                },
                                            ],
                                            "must": [
                                                {
                                                    "term": {
                                                        "samples_num_alt_2": "NA12878"
                                                    }
                                                }
                                            ],
                                        }
                                    }
                                ],
                                "_name": "F000001_trio",
                            }
                        },
                    ]
                }
            },
            "sort": ["xpos", "variantId"],
            "from": 0,
            "size": 100,
            "_source": [],
        }

    def test_denovo_dominant_pathogenic(self):
        search_model_dict = {
            "pathogenicity": {"clinvar": ["pathogenic", "likely_pathogenic"]},
            "inheritance": {
                "mode": "de_novo",
                "filter": {"A": "has_alt", "N": "ref_ref"},
                "annotationSecondary": False,
            },
        }

        family_ids = ["F000001_trio"]

        search_model = SearchModel(**search_model_dict)

        constructor = QueryConstructor(backend=TestBackend())
        expression = constructor.build_expression_from(
            search_model,
            samples_by_family_index=get_samples_by_family_index(families=family_ids),
            indices=["na12878-trio"],
        )

        sql = expression.output_sql("variants")
        # SELECT * FROM variants WHERE (clinvar_clinical_significance in ("Likely_pathogenic", "Pathogenic", "Pathogenic/Likely_pathogenic") AND (((samples_num_alt_1 = "NA12878" OR samples_num_alt_2 = "NA12878") AND NOT (samples_no_call = "NA12891" OR samples_num_alt_1 = "NA12891" OR samples_num_alt_2 = "NA12891"))))
        print(sql)

        protobuf = expression.output_protobuf(fields=[], arrow_urls=[])
        print(protobuf)

        es = expression.output_elasticsearch([], 0, 1000, source=["xpos", "variantId"])
        es_expected = {
            "bool": {
                "filter": [
                    {
                        "terms": {
                            "clinvar_clinical_significance": [
                                "Likely_pathogenic",
                                "Pathogenic",
                                "Pathogenic/Likely_pathogenic",
                            ]
                        }
                    },
                    {
                        "bool": {
                            "must": [
                                {
                                    "bool": {
                                        "should": [
                                            {"term": {"samples_num_alt_1": "NA12878"}},
                                            {"term": {"samples_num_alt_2": "NA12878"}},
                                        ],
                                        "must_not": [
                                            {"term": {"samples_no_call": "NA12891"}},
                                            {"term": {"samples_num_alt_1": "NA12891"}},
                                            {"term": {"samples_num_alt_2": "NA12891"}},
                                        ],
                                        "minimum_should_match": 1,
                                    }
                                }
                            ],
                            "_name": "F000001_trio",
                        }
                    },
                ]
            }
        }
