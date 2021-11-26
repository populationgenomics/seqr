from enum import Enum
from typing import Dict, List


class DatasetType(Enum):
    VARIANT_CALLS = "VARIANTS"
    SV_CALLS = "SV"


class SearchModel:
    def __init__(
        self,
        inheritance=None,
        quality_filter=None,
        annotations=None,
        annotations_secondary=None,
        pathogenicity: Dict[str, List[str]] = None,
        skip_genotype_filter=None,
        freqs=None,
        custom_query=None,
    ):
        """
        :param pathogenicity: Dict with keys {"clinvar": [CLINVAR_SIGNFICANCE_MAP values], "hgmd": [HGMD_CLASS_MAP values]}
        """
        self.pathogenicity = pathogenicity
        self.inheritance = inheritance
        self.quality_filter = quality_filter
        self.annotations = annotations
        self.annotations_secondary = annotations_secondary
        self.skip_genotype_filter = skip_genotype_filter
        self.freqs = freqs

        if custom_query:
            raise NotImplementedError(f"Unsupported customQuery: {custom_query}")
        self.custom_query = custom_query

    @staticmethod
    def from_dict(d):
        return SearchModel(
            inheritance=d.get("inheritance"),
            quality_filter=d.get("qualityFilter"),
            annotations=d.get("annotations"),
            annotations_secondary=d.get("annotations_secondary"),
            pathogenicity=d.get("pathogenicity"),
            skip_genotype_filter=d.get("skip_genotype_filter"),
            freqs=d.get("freqs"),
            custom_query=d.get("customQuery"),
        )
