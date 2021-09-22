import json
import os
import django
from django.test import TestCase

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from ...models import Sample, Family
from .constructor import SearchModel, build_expression_from


class TestPathogenicity(TestCase):
    def test_pathogenic(self):
        search_model = SearchModel(
            **{"pathogenicity": {"clinvar": ["pathogenic", "likely_pathogenic"]}}
        )
        expression = build_expression_from(search_model)
        s = expression.output_protobuff(fields=[], arrow_urls=[])
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
            "query": {
                "bool": {
                    "filter": {
                        "terms": {
                            "clinvar_clinical_significance": [
                                "Likely_pathogenic",
                                "Pathogenic",
                                "Pathogenic/Likely_pathogenic",
                            ]
                        }
                    }
                }
            },
            "sort": ["xpos", "variantId"],
            "from": 0,
            "size": 100,
            "_source": [],
        }

        self.assertDictEqual(expected, es)

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

        families = Family.objects.filter(guid__in=['F000001_trio'])
        samples = Sample.objects.filter(is_active=True, individual__family__in=families)

        search_model = SearchModel(**search_model_dict)

        expression = build_expression_from(search_model, indices=['na12878-trio'], samples=samples)

        protobuff = expression.output_protobuff(fields=[], arrow_urls=[])
        print(protobuff)

        es_expected = {
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
