from copy import deepcopy
from collections import defaultdict

from reference_data.models import GENOME_VERSION_GRCh37, GENOME_VERSION_GRCh38
from seqr.models import Sample, Individual
from seqr.utils.elasticsearch.es_search import (
    _liftover_grch38_to_grch37,
    _liftover_grch37_to_grch38,
)
from seqr.utils.search.backend import Backend
from seqr.utils.search.expression import *
from seqr.utils.xpos_utils import get_xpos, MIN_POS, MAX_POS
from seqr.utils.elasticsearch.constants import (
    CLINVAR_SIGNFICANCE_MAP,
    HGMD_CLASS_MAP,
    QUALITY_FIELDS,
    RECESSIVE,
    COMPOUND_HET,
    ANY_AFFECTED,
    INHERITANCE_FILTERS,
    GENOTYPE_QUERY_MAP,
    REF_REF,
    X_LINKED_RECESSIVE,
)
from seqr.utils.search.models import SearchModel


# handy functions

def get_samples_by_family_index(families: List[str]) -> Dict[str, Dict[str, Dict[str, Sample]]]:
    samples = Sample.objects.filter(
        is_active=True, individual__family__guid__in=families
    )

    _samples_by_family_index = defaultdict(lambda: defaultdict(dict))
    for s in samples.select_related("individual__family"):
        _samples_by_family_index[s.elasticsearch_index][s.individual.family.guid][
            s.sample_id
        ] = s

    return _samples_by_family_index


# okay, let's go!!

class QueryConstructor:
    """
    Turns a SearchModel into an Expression, using data from the backend
    """

    def __init__(self, backend: Backend):
        self.backend: Backend = backend

    def build_expression_from(
        self,
        search_model: SearchModel,
        # I personally think it's dangerous to use positional arguments for this function
        *,
        indices: List[str],
        samples_by_family_index: Dict[str, Dict[str, Dict[str, Sample]]],
    ) -> Expression:
        """
        Where the magic happens ;)

        :param search_model: Search model the drives the query
        :param indices: list of database indices (collections / tables)
        :param samples_by_family_index: see `get_samples_by_family_index(families)`
        :type samples_by_family_index: Dict[ESIndex, Dict[FamilyGuid, Dict[SampleId, Sample]]]
        :indices: A list of ES indices (or equivalent) to query against
        """
        _indices_by_dataset_type = defaultdict(list)
        # _index_searches = defaultdict(list)

        _family_individual_affected_status = {}

        filters = []

        # customQuery NOT IMPLEMENTED
        # if search_model.customQuery:
        #     if not isinstance(search_model.customQuery, list):
        #         custom_q = [search_model.customQuery]
        #     for q_dict in search_model.customQuery:
        #         # how to convert Dict to Expression
        #         filters.append(q_dict)

        if search_model.inheritance is not None:
            (
                samples_by_family_index,
                _family_individual_affected_status,
            ) = self.filter_families_for_inheritance(
                inheritance=search_model.inheritance,
                samples_by_family_index=samples_by_family_index,
            )
            if len(samples_by_family_index) < 1:
                # raise InvalidSearchException(
                raise Exception(
                    "Inheritance based search is disabled in families with no data loaded for affected individuals"
                )

        filters.append(
            self.filter_by_annotation_and_genotype(
                samples_by_family_index=samples_by_family_index,
                indices=indices,
                family_individual_affected_status=_family_individual_affected_status,
                # other params
                inheritance=search_model.inheritance,
                quality_filter=search_model.quality_filter,
                annotations=search_model.annotations,
                annotations_secondary=search_model.annotations_secondary,
                pathogenicity=search_model.pathogenicity,
                skip_genotype_filter=search_model.skip_genotype_filter,
            )
        )

        return filters[0] if len(filters) == 1 else CallAnd(*filters)

    def filter_by_annotation_and_genotype(
        self,
        *,
        samples_by_family_index,
        family_individual_affected_status,
        # other params
        indices,
        inheritance,
        quality_filter=None,
        annotations=None,
        annotations_secondary=None,
        pathogenicity=None,
        skip_genotype_filter=False,
    ):
        # has_previous_compound_hets = self.previous_search_results.get('grouped_results')

        filters = []

        inheritance_mode = (inheritance or {}).get("mode")
        inheritance_filter = (inheritance or {}).get("filter") or {}
        if inheritance_filter.get("genotype"):
            inheritance_mode = None

        if quality_filter and quality_filter.get("vcf_filter") is not None:
            filters.append(CallExists(Field("filters")))
            # self.filter(~Q('exists', field='filters'))

        annotations_secondary_search = None
        secondary_dataset_type = None
        allowed_consequences_secondary = None

        if annotations_secondary:
            annotations_filter, _ = self.annotations_filter(annotations or {})
            (
                annotations_secondary_filter,
                allowed_consequences_secondary,
            ) = self.annotations_filter(annotations_secondary)

            annotations_secondary_search = annotations_filter.or_(
                annotations_secondary_filter
            )
            # annotations_secondary_search = self._search.filter(annotations_filter | annotations_secondary_filter)
            # _allowed_consequences_secondary = allowed_consequences_secondary
            # secondary_dataset_type = _dataset_type_for_annotations(annotations_secondary)

        pathogenicity_filter = self.pathogenicity_filter(pathogenicity or {})
        if annotations or pathogenicity_filter:
            # _filter = self.
            _filter = self.by_annotations_filter(annotations, pathogenicity_filter)
            if _filter:
                filters.append(_filter)
            # dataset_type = _filter_by_annotations(annotations, pathogenicity_filter)
            # if dataset_type is None or dataset_type == secondary_dataset_type:
            #     secondary_dataset_type = None

        # if secondary_dataset_type:
        #     self.update_dataset_type(secondary_dataset_type, keep_previous=True)

        if skip_genotype_filter:
            return

        quality_filters_by_family = self.quality_filters_by_family(
            quality_filter, samples_by_family_index, indices
        )

        if inheritance_mode in {
            RECESSIVE,
            COMPOUND_HET,
        }:  # and not has_previous_compound_hets:
            raise NotImplementedError
            self.filter_compound_hets(
                quality_filters_by_family, annotations_secondary_search
            )
            if inheritance_mode == COMPOUND_HET:
                return

        expr = self.by_genotype_filters(
            indices=indices,
            indices_by_dataset_type=None,
            samples_by_family_index=samples_by_family_index,
            index_metadata=None,
            family_individual_affected_status=family_individual_affected_status,
            # other params
            inheritance_mode=inheritance_mode,
            inheritance_filter=inheritance_filter,
            quality_filters_by_family=quality_filters_by_family,
            secondary_dataset_type=secondary_dataset_type,
        )
        if expr:
            filters.append(expr)
        return CallAnd(*filters)

    def filter_families_for_inheritance(
        self, inheritance: Dict, samples_by_family_index
    ):
        _family_individual_affected_status = {}
        _skipped_sample_count = defaultdict(int)

        _samples_by_family_index = deepcopy(samples_by_family_index)

        for index, family_samples in list(_samples_by_family_index.items()):
            index_skipped_families = []
            for family_guid, samples_by_id in family_samples.items():
                individual_affected_status = self.get_family_affected_status(
                    samples_by_id, inheritance.get("filter") or {}
                )

                has_affected_samples = any(
                    aftd == Individual.AFFECTED_STATUS_AFFECTED
                    for aftd in individual_affected_status.values()
                )
                if not has_affected_samples:
                    index_skipped_families.append(family_guid)

                    _skipped_sample_count[index] += len(samples_by_id)

                if family_guid not in _family_individual_affected_status:
                    _family_individual_affected_status[family_guid] = {}
                _family_individual_affected_status[family_guid].update(
                    individual_affected_status
                )

            for family_guid in index_skipped_families:
                del _samples_by_family_index[index][family_guid]

            if not _samples_by_family_index[index]:
                del _samples_by_family_index[index]

        return _samples_by_family_index, _family_individual_affected_status

    def by_location_filter(
        self, genes=None, intervals=None, rs_ids=None, variant_ids=None, locus=None
    ) -> Expression:
        genome_version = locus and locus.get("genomeVersion")
        variant_id_genome_versions = {
            variant_id: genome_version for variant_id in variant_ids or []
        }
        if variant_id_genome_versions and genome_version:
            lifted_genome_version = (
                GENOME_VERSION_GRCh37
                if genome_version == GENOME_VERSION_GRCh38
                else GENOME_VERSION_GRCh38
            )
            liftover = (
                _liftover_grch38_to_grch37()
                if genome_version == GENOME_VERSION_GRCh38
                else _liftover_grch37_to_grch38()
            )
            if liftover:
                for variant_id in deepcopy(variant_ids):
                    chrom, pos, ref, alt = self.parse_variant_id(variant_id)
                    lifted_coord = liftover.convert_coordinate(
                        "chr{}".format(chrom), pos
                    )
                    if lifted_coord and lifted_coord[0]:
                        lifted_variant_id = "{chrom}-{pos}-{ref}-{alt}".format(
                            chrom=lifted_coord[0][0].lstrip("chr"),
                            pos=lifted_coord[0][1],
                            ref=ref,
                            alt=alt,
                        )
                        variant_id_genome_versions[
                            lifted_variant_id
                        ] = lifted_genome_version
                        variant_ids.append(lifted_variant_id)

        filter = self.location_filter(genes, intervals, rs_ids, variant_ids, locus)
        if (
            not (genes or intervals or rs_ids)
            and len(
                {
                    genome_version
                    for genome_version in variant_id_genome_versions.values()
                }
            )
            > 1
        ):
            raise NotImplementedError(
                'Side effect of querying by location "_filtered_variant_ids"'
            )
            # self._filtered_variant_ids = variant_id_genome_versions
        return filter

    def location_filter(self, genes, intervals, rs_ids, variant_ids, location_filter):
        # TODO
        raise NotImplementedError
        q = None
        if intervals:
            for interval in intervals:
                if interval.get("offset"):
                    offset_pos = int(
                        (interval["end"] - interval["start"]) * interval["offset"]
                    )
                    interval_q = Q(
                        "range",
                        xpos=_pos_offset_range_filter(
                            interval["chrom"], interval["start"], offset_pos
                        ),
                    ) & Q(
                        "range",
                        xstop=_pos_offset_range_filter(
                            interval["chrom"], interval["end"], offset_pos
                        ),
                    )
                else:
                    xstart = get_xpos(interval["chrom"], interval["start"])
                    xstop = get_xpos(interval["chrom"], interval["end"])
                    range_filters = [
                        {
                            key: {
                                "gte": xstart,
                                "lte": xstop,
                            }
                        }
                        for key in ["xpos", "xstop"]
                    ]
                    interval_q = self.build_or_filter("range", range_filters)
                    interval_q |= Q("range", xpos={"lte": xstart}) & Q(
                        "range", xstop={"gte": xstop}
                    )

                if q:
                    q |= interval_q
                else:
                    q = interval_q

        filters = [
            {"geneIds": list((genes or {}).keys())},
            {"rsid": rs_ids},
            {"variantId": variant_ids},
        ]
        filters = [f for f in filters if next(iter(f.values()))]
        if filters:
            location_q = self.build_or_filter("terms", filters)
            if q:
                q |= location_q
            else:
                q = location_q

        if location_filter and location_filter.get("excludeLocations"):
            return ~q
        else:
            return q

    def by_annotations_filter(
        self, annotations: Dict[str, List[str]], pathogenicity_filter: Expression
    ) -> Expression:
        dataset_type = None
        consequences_filter, allowed_consequences = self.annotations_filter(
            annotations or {}
        )
        if allowed_consequences:
            if pathogenicity_filter:
                # Pathogencicity and transcript consequences act as "OR" filters instead of the usual "AND"
                consequences_filter = consequences_filter.or_(pathogenicity_filter)

            return consequences_filter
        elif pathogenicity_filter:
            return pathogenicity_filter

        return None

    def by_genotype_filters(
            self,
        *,
        indices: List[str],
        indices_by_dataset_type: Dict[str, List[str]],
        samples_by_family_index: Dict[str, Dict[str, Dict[str, Sample]]],
        index_metadata,
        family_individual_affected_status: Dict[str, Dict[str, str]],
        # other params
        inheritance_mode: str,
        inheritance_filter: Dict[str, str],
        quality_filters_by_family: Dict[str, Expression],
        secondary_dataset_type: any,
    ):
        # TODO:
        _skipped_sample_count = defaultdict(int)

        # start
        has_inheritance_filter = inheritance_filter or inheritance_mode
        all_sample_search = (not quality_filters_by_family) and (
            inheritance_mode == ANY_AFFECTED or not has_inheritance_filter
        )
        no_filter_indices = set()

        if secondary_dataset_type:
            raise NotImplementedError
            secondary_only_indices = indices_by_dataset_type[secondary_dataset_type]
            indices = [
                index for index in indices if index not in secondary_only_indices
            ]

        for index in indices:
            family_samples_by_id: Dict[
                str, Dict[str, Sample]
            ] = samples_by_family_index[index]
            index_fields = []  # index_metadata[index]["fields"]
            index_fields = {
                "AC": "integer",
                "AF": "double",
                "AN": "integer",
                "aIndex": "integer",
                "alt": "keyword",
                "cadd_PHRED": "float",
                "clinvar_allele_id": "integer",
                "clinvar_clinical_significance": "keyword",
                "clinvar_gold_stars": "integer",
                "codingGeneIds": "keyword",
                "contig": "keyword",
                "dbnsfp_FATHMM_pred": "keyword",
                "dbnsfp_GERP_RS": "keyword",
                "dbnsfp_MetaSVM_pred": "keyword",
                "dbnsfp_MutationTaster_pred": "keyword",
                "dbnsfp_Polyphen2_HVAR_pred": "keyword",
                "dbnsfp_REVEL_score": "keyword",
                "dbnsfp_SIFT_pred": "keyword",
                "dbnsfp_phastCons100way_vertebrate": "keyword",
                "docId": "keyword",
                "domains": "keyword",
                "eigen_Eigen_phred": "double",
                "end": "integer",
                "exac_AC_Adj": "integer",
                "exac_AC_Hemi": "integer",
                "exac_AC_Het": "integer",
                "exac_AC_Hom": "integer",
                "exac_AF": "double",
                "exac_AF_POPMAX": "double",
                "exac_AN_Adj": "integer",
                "filters": "keyword",
                "g1k_AC": "integer",
                "g1k_AF": "double",
                "g1k_AN": "integer",
                "g1k_POPMAX_AF": "double",
                "geneIds": "keyword",
                "geno2mp_HPO_Count": "integer",
                "genotypes": "nested",
                "gnomad_exome_coverage": "double",
                "gnomad_exomes_AC": "integer",
                "gnomad_exomes_AF": "double",
                "gnomad_exomes_AF_POPMAX_OR_GLOBAL": "double",
                "gnomad_exomes_AN": "integer",
                "gnomad_exomes_FAF_AF": "double",
                "gnomad_exomes_Hemi": "integer",
                "gnomad_exomes_Hom": "integer",
                "gnomad_genome_coverage": "double",
                "gnomad_genomes_AC": "integer",
                "gnomad_genomes_AF": "double",
                "gnomad_genomes_AF_POPMAX_OR_GLOBAL": "double",
                "gnomad_genomes_AN": "integer",
                "gnomad_genomes_FAF_AF": "double",
                "gnomad_genomes_Hemi": "integer",
                "gnomad_genomes_Hom": "integer",
                "mainTranscript_amino_acids": "keyword",
                "mainTranscript_biotype": "keyword",
                "mainTranscript_canonical": "integer",
                "mainTranscript_category": "keyword",
                "mainTranscript_cdna_end": "integer",
                "mainTranscript_cdna_start": "integer",
                "mainTranscript_codons": "keyword",
                "mainTranscript_domains": "keyword",
                "mainTranscript_gene_id": "keyword",
                "mainTranscript_gene_symbol": "keyword",
                "mainTranscript_hgvs": "keyword",
                "mainTranscript_hgvsc": "keyword",
                "mainTranscript_hgvsp": "keyword",
                "mainTranscript_lof": "keyword",
                "mainTranscript_lof_filter": "keyword",
                "mainTranscript_lof_flags": "keyword",
                "mainTranscript_lof_info": "keyword",
                "mainTranscript_major_consequence": "keyword",
                "mainTranscript_major_consequence_rank": "integer",
                "mainTranscript_polyphen_prediction": "keyword",
                "mainTranscript_protein_id": "keyword",
                "mainTranscript_sift_prediction": "keyword",
                "mainTranscript_transcript_id": "keyword",
                "mpc_MPC": "keyword",
                "originalAltAlleles": "keyword",
                "pos": "integer",
                "primate_ai_score": "double",
                "ref": "keyword",
                "rg37_locus": None,
                "rsid": "keyword",
                "samples_ab_0_to_5": "keyword",
                "samples_ab_10_to_15": "keyword",
                "samples_ab_15_to_20": "keyword",
                "samples_ab_20_to_25": "keyword",
                "samples_ab_25_to_30": "keyword",
                "samples_ab_30_to_35": "keyword",
                "samples_ab_35_to_40": "keyword",
                "samples_ab_40_to_45": "keyword",
                "samples_ab_5_to_10": "keyword",
                "samples_gq_0_to_5": "keyword",
                "samples_gq_10_to_15": "keyword",
                "samples_gq_15_to_20": "keyword",
                "samples_gq_20_to_25": "keyword",
                "samples_gq_25_to_30": "keyword",
                "samples_gq_30_to_35": "keyword",
                "samples_gq_35_to_40": "keyword",
                "samples_gq_40_to_45": "keyword",
                "samples_gq_45_to_50": "keyword",
                "samples_gq_50_to_55": "keyword",
                "samples_gq_55_to_60": "keyword",
                "samples_gq_5_to_10": "keyword",
                "samples_gq_60_to_65": "keyword",
                "samples_gq_65_to_70": "keyword",
                "samples_gq_70_to_75": "keyword",
                "samples_gq_75_to_80": "keyword",
                "samples_gq_80_to_85": "keyword",
                "samples_gq_85_to_90": "keyword",
                "samples_gq_90_to_95": "keyword",
                "samples_no_call": "keyword",
                "samples_num_alt_1": "keyword",
                "samples_num_alt_2": "keyword",
                "sortedTranscriptConsequences": "nested",
                "splice_ai_delta_score": "float",
                "splice_ai_splice_consequence": "keyword",
                "start": "integer",
                "topmed_AC": "integer",
                "topmed_AF": "double",
                "topmed_AN": "integer",
                "topmed_Het": "integer",
                "topmed_Hom": "integer",
                "transcriptConsequenceTerms": "keyword",
                "transcriptIds": "keyword",
                "variantId": "keyword",
                "wasSplit": "boolean",
                "xpos": "long",
                "xstart": "long",
                "xstop": "long",
            }
            genotypes_q = None
            if all_sample_search:
                search_sample_count = (
                    sum(len(samples) for samples in family_samples_by_id.values())
                    + _skipped_sample_count[index]
                )
                index_sample_count = Sample.objects.filter(
                    elasticsearch_index=index, is_active=True
                ).count()
                if search_sample_count == index_sample_count:
                    if inheritance_mode == ANY_AFFECTED:
                        sample_ids = []
                        for family_guid, samples_by_id in family_samples_by_id.items():
                            sample_ids += [
                                sample_id
                                for sample_id, sample in samples_by_id.items()
                                if family_individual_affected_status[family_guid][
                                    sample.individual.guid
                                ]
                                == Individual.AFFECTED_STATUS_AFFECTED
                            ]
                        genotypes_q = self.any_affected_sample_filter(sample_ids)
                        # self.self.any_affected_sample_filters = True
                    else:
                        # If searching across all families in an index with no inheritance mode we do not need to explicitly
                        # filter on inheritance, as all variants have some inheritance for at least one family
                        # self._no_sample_filters = True
                        no_filter_indices.add(index)
                        continue

            if not genotypes_q:
                for family_guid in sorted(family_samples_by_id.keys()):
                    family_samples_q = _get_family_sample_query(
                        family_individual_affected_status=family_individual_affected_status,
                        family_guid=family_guid,
                        family_samples_by_id=family_samples_by_id,
                        quality_filters_by_family=quality_filters_by_family,
                        index_fields=index_fields,
                        inheritance_mode=inheritance_mode,
                        inheritance_filter=inheritance_filter,
                    )
                    if not genotypes_q:
                        genotypes_q = family_samples_q
                    else:
                        genotypes_q |= family_samples_q

        #     self._index_searches[index].append(self._search.filter(genotypes_q))
        #
        # if no_filter_indices and self._index_searches:
        #     for index in no_filter_indices:
        #         self._index_searches[index].append(self._search)

        return genotypes_q

    def annotations_filter(
        self, annotations: Dict[str, List[str]]
    ) -> Tuple[Expression, List[str]]:
        vep_consequences: List[str] = sorted(
            [ann for anns in annotations.values() for ann in anns]
        )
        consequences_filter = CallFieldIsOneOf(
            Field("transcriptConsequenceTerms"), vep_consequences
        )
        # consequences_filter = Q('terms', transcriptConsequenceTerms=vep_consequences)

        if "intergenic_variant" in vep_consequences:
            # VEP doesn't add annotations for many intergenic variants so match variants where no transcriptConsequenceTerms
            consequences_filter = consequences_filter.or_(
                CallExists(Field("transcriptConsequenceTerms"))
            )
            # ~Q('exists', field='transcriptConsequenceTerms')

        return consequences_filter, vep_consequences

    def pathogenicity_filter(self, pathogenicity: Dict[str, any]) -> Expression:
        clinvar_filters = pathogenicity.get("clinvar", [])
        hgmd_filters = pathogenicity.get("hgmd", [])

        pathogenicity_filter: Optional[Expression] = None
        if clinvar_filters:
            clinvar_clinical_significance_terms = set()
            for clinvar_filter in clinvar_filters:
                clinvar_clinical_significance_terms.update(
                    CLINVAR_SIGNFICANCE_MAP.get(clinvar_filter, [])
                )

            options = sorted(list(clinvar_clinical_significance_terms))
            pathogenicity_filter = CallFieldIsOneOf(
                Field("clinvar_clinical_significance"), options
            )

        if hgmd_filters:
            hgmd_class = set()
            for hgmd_filter in hgmd_filters:
                hgmd_class.update(HGMD_CLASS_MAP.get(hgmd_filter, []))

            options = sorted(list(hgmd_class))
            hgmd_filter = CallFieldIsOneOf(Field("hgmd_class"), options)
            if pathogenicity_filter:
                pathogenicity_filter = pathogenicity_filter.or_(hgmd_filter)
            else:
                pathogenicity_filter = hgmd_filter

        return pathogenicity_filter

    def quality_filters_by_family(
        self, quality_filter, samples_by_family_index, indices
    ) -> Dict[str, Expression]:
        quality_field_configs = {
            f"min_{field}": {"field": field, "step": step}
            for field, step in QUALITY_FIELDS.items()
        }
        quality_filter = dict(
            {field: 0 for field in quality_field_configs.keys()},
            **(quality_filter or {}),
        )
        for field, config in quality_field_configs.items():
            if quality_filter[field] % config["step"] != 0:
                raise Exception(
                    f'Invalid {config["field"]} filter {quality_filter[field]}'
                )

        quality_filters_by_family = {}
        if any(quality_filter[field] for field in quality_field_configs.keys()):
            family_sample_ids = defaultdict(set)
            for index in indices:
                family_samples_by_id = samples_by_family_index[index]
                for family_guid, samples_by_id in family_samples_by_id.items():
                    family_sample_ids[family_guid].update(samples_by_id.keys())

            for family_guid, sample_ids in sorted(family_sample_ids.items()):
                family_filters = []
                for sample_id in sorted(sample_ids):
                    for field, config in sorted(quality_field_configs.items()):
                        if quality_filter[field]:
                            q = CallOr(
                                *[
                                    CallEqual(
                                        Field(
                                            f'samples_{config["field"]}_{i}_to_{i + config["step"]}'
                                        ),
                                        sample_id,
                                    )
                                    for i in range(
                                        0, quality_filter[field], config["step"]
                                    )
                                ],
                            )
                            if field == "min_ab":
                                # AB only relevant for hets
                                # mfranklin: simplfied this from the original
                                # !A | !B == A && B
                                # quality_q &= ~Q(q) | ~Q('term', samples_num_alt_1=sample_id)

                                family_filters.append(q)
                                family_filters.append(
                                    CallEqual(Field("samples_num_alt_1"), sample_id)
                                )
                            else:
                                # quality_q &= ~Q(q)
                                family_filters.append(q.negate())

                quality_filters_by_family[family_guid] = CallAnd(*family_filters)

        return quality_filters_by_family

    def any_affected_sample_filter(self, sample_ids: List[str]) -> Expression:
        sample_ids = sorted(sample_ids)
        return CallOr(
            CallFieldIsOneOf(field=Field("samples_num_alt_1"), values=sample_ids),
            CallFieldIsOneOf(field=Field("samples_num_alt_2"), values=sample_ids),
            CallFieldIsOneOf(field=Field("samples"), values=sample_ids),
        )
        # return
        #   Q('terms', samples_num_alt_1=sample_ids)
        #   | Q('terms', samples_num_alt_2=sample_ids)
        #   | Q('terms', samples=sample_ids)

    def get_family_sample_query(
        self,
        *,
        family_individual_affected_status,
        # other params
        family_guid,
        family_samples_by_id,
        quality_filters_by_family: Dict[str, Expression],
        index_fields,
        inheritance_mode,
        inheritance_filter,
    ) -> Expression:
        samples_by_id = family_samples_by_id[family_guid]
        affected_status = family_individual_affected_status.get(family_guid)

        # Filter samples by inheritance
        if inheritance_mode == ANY_AFFECTED:
            # Only return variants where at least one of the affected samples has an alt allele
            sample_ids = [
                sample_id
                for sample_id, sample in samples_by_id.items()
                if affected_status[sample.individual.guid]
                == Individual.AFFECTED_STATUS_AFFECTED
            ]
            family_samples_q = self.any_affected_sample_filter(sample_ids)
        elif inheritance_filter or inheritance_mode:
            if inheritance_mode:
                inheritance_filter.update(INHERITANCE_FILTERS[inheritance_mode])

            if list(inheritance_filter.keys()) == ["affected"]:
                from seqr.utils.elasticsearch.utils import InvalidSearchException

                raise InvalidSearchException(
                    "Inheritance must be specified if custom affected status is set"
                )

            family_samples_q = self.family_genotype_inheritance_filter(
                inheritance_mode,
                inheritance_filter,
                samples_by_id,
                affected_status,
                index_fields,
            )

            # For recessive search, should be hom recessive, x-linked recessive, or compound het
            if inheritance_mode == RECESSIVE:
                x_linked_q = self.family_genotype_inheritance_filter(
                    X_LINKED_RECESSIVE,
                    inheritance_filter,
                    samples_by_id,
                    affected_status,
                    index_fields,
                )
                family_samples_q |= x_linked_q
        else:
            # If no inheritance specified only return variants where at least one of the requested samples has an alt allele
            family_samples_q = self.any_affected_sample_filter(
                list(samples_by_id.keys())
            )

        return self.named_family_sample_q(
            family_samples_q, family_guid, quality_filters_by_family
        )

    def family_genotype_inheritance_filter(
        self,
        inheritance_mode,
        inheritance_filter,
        samples_by_id,
        individual_affected_status,
        index_fields,
    ):
        samples_q = None

        individuals = [sample.individual for sample in samples_by_id.values()]

        individual_genotype_filter = inheritance_filter.get("genotype") or {}

        if inheritance_mode == X_LINKED_RECESSIVE:
            # samples_q = Q('match', contig='X')
            samples_q = CallEqual(Field("contig"), Literal("X"))
            for individual in individuals:
                if (
                    individual_affected_status[individual.guid]
                    == Individual.AFFECTED_STATUS_UNAFFECTED
                    and individual.sex == Individual.SEX_MALE
                ):
                    individual_genotype_filter[individual.guid] = REF_REF

        is_sv_comp_het = inheritance_mode == COMPOUND_HET and "samples" in index_fields
        for sample_id, sample in sorted(samples_by_id.items()):

            individual_guid = sample.individual.guid
            affected = individual_affected_status[individual_guid]

            genotype = individual_genotype_filter.get(
                individual_guid
            ) or inheritance_filter.get(affected)

            if genotype:
                if is_sv_comp_het and affected == Individual.AFFECTED_STATUS_UNAFFECTED:
                    # Unaffected individuals for SV compound het search can have any genotype so are not included
                    continue

                not_allowed_num_alt = [
                    num_alt
                    for num_alt in GENOTYPE_QUERY_MAP[genotype].get(
                        "not_allowed_num_alt", []
                    )
                    if num_alt in index_fields
                ]
                allowed_num_alt = [
                    num_alt
                    for num_alt in GENOTYPE_QUERY_MAP[genotype].get(
                        "allowed_num_alt", []
                    )
                    if num_alt in index_fields
                ]
                num_alt_to_filter = not_allowed_num_alt or allowed_num_alt
                sample_filters = [
                    CallEqual(Field(num_alt_key), Literal(sample_id))
                    for num_alt_key in num_alt_to_filter
                ]

                # sample_q = self.build_or_filter('term', sample_filters)
                sample_q = CallOr(*sample_filters)
                if not_allowed_num_alt:
                    # sample_q = ~Q(sample_q)
                    sample_q = CallNegate(sample_q)

                if not samples_q:
                    samples_q = sample_q
                else:
                    samples_q = samples_q.and_(sample_q)

        return samples_q

    def named_family_sample_q(
        self,
        family_samples_q,
        family_guid,
        quality_filters_by_family: Dict[str, Expression],
    ) -> Expression:
        sample_queries = [family_samples_q]
        quality_q = quality_filters_by_family.get(family_guid)
        if quality_q:
            sample_queries.append(quality_q)

        return CallAnd(*sample_queries)
        # return Q('bool', must=sample_queries, _name=family_guid)

    def get_family_affected_status(self, samples_by_id, inheritance_filter: Dict):
        individual_affected_status = inheritance_filter.get("affected") or {}
        affected_status = {}
        for sample in samples_by_id.values():
            indiv = sample.individual
            affected_status[indiv.guid] = (
                individual_affected_status.get(indiv.guid) or indiv.affected
            )

        return affected_status
