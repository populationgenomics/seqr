from aiohttp.web import HTTPBadRequest, HTTPNotFound
from collections import defaultdict, namedtuple
import hail as hl
import logging
import os

from hail_search.constants import AFFECTED, AFFECTED_ID, ALT_ALT, ANNOTATION_OVERRIDE_FIELDS, ANY_AFFECTED, COMP_HET_ALT, \
    COMPOUND_HET, GENOME_VERSION_GRCh38, GROUPED_VARIANTS_FIELD, ALLOWED_TRANSCRIPTS, ALLOWED_SECONDARY_TRANSCRIPTS,  HAS_ANNOTATION_OVERRIDE, \
    HAS_ALT, HAS_REF,INHERITANCE_FILTERS, PATH_FREQ_OVERRIDE_CUTOFF, MALE, RECESSIVE, REF_ALT, REF_REF, UNAFFECTED, \
    UNAFFECTED_ID, X_LINKED_RECESSIVE, XPOS, OMIM_SORT, UNKNOWN_AFFECTED, UNKNOWN_AFFECTED_ID, FAMILY_GUID_FIELD, GENOTYPES_FIELD, \
    AFFECTED_ID_MAP

DATASETS_DIR = os.environ.get('DATASETS_DIR', '/hail_datasets')
SSD_DATASETS_DIR = os.environ.get('SSD_DATASETS_DIR', DATASETS_DIR)

logger = logging.getLogger(__name__)


PredictionPath = namedtuple('PredictionPath', ['source', 'field', 'format'], defaults=[lambda x: x])
QualityFilterFormat = namedtuple('QualityFilterFormat', ['scale', 'override'], defaults=[None, None])


def _to_camel_case(snake_case_str):
    converted = snake_case_str.replace('_', ' ').title().replace(' ', '')
    return converted[0].lower() + converted[1:]


class BaseHailTableQuery(object):

    DATA_TYPE = None
    KEY_FIELD = None
    LOADED_GLOBALS = None

    GENOTYPE_QUERY_MAP = {
        REF_REF: lambda gt: gt.is_hom_ref(),
        REF_ALT: lambda gt: gt.is_het(),
        COMP_HET_ALT: lambda gt: gt.is_het(),
        ALT_ALT: lambda gt: gt.is_hom_var(),
        HAS_ALT: lambda gt: gt.is_non_ref(),
        HAS_REF: lambda gt: gt.is_hom_ref() | gt.is_het_ref(),
    }
    MISSING_NUM_ALT = -1

    GENOTYPE_FIELDS = {}
    COMPUTED_GENOTYPE_FIELDS = {}
    GENOTYPE_OVERRIDE_FIELDS = {}
    GENOTYPE_QUERY_FIELDS = {}
    QUALITY_FILTER_FORMAT = {}
    POPULATIONS = {}
    POPULATION_FIELDS = {}
    POPULATION_KEYS = ['AF', 'AC', 'AN', 'Hom', 'Hemi', 'Het']
    PREDICTION_FIELDS_CONFIG = {}
    ANNOTATION_OVERRIDE_FIELDS = []
    SECONDARY_ANNOTATION_OVERRIDE_FIELDS = None

    GENOME_VERSION = GENOME_VERSION_GRCh38
    GLOBALS = ['enums']
    TRANSCRIPTS_FIELD = None
    CORE_FIELDS = [XPOS]
    BASE_ANNOTATION_FIELDS = {
        FAMILY_GUID_FIELD: lambda r: r.family_entries.filter(hl.is_defined).map(lambda entries: entries.first().familyGuid),
        'genotypeFilters': lambda r: hl.str(' ,').join(r.filters),
        'variantId': lambda r: r.variant_id,
    }
    ENUM_ANNOTATION_FIELDS = {
        'transcripts': {
            'response_key': 'transcripts',
            'empty_array': True,
            'format_value': lambda value: value.rename({k: _to_camel_case(k) for k in value.keys()}),
            'format_array_values': lambda values, *args: values.group_by(lambda t: t.geneId),
        },
    }
    LIFTOVER_ANNOTATION_FIELDS = {
        'liftedOverGenomeVersion': lambda r: hl.or_missing(hl.is_defined(r.rg37_locus), '37'),
        'liftedOverChrom': lambda r: hl.or_missing(hl.is_defined(r.rg37_locus), r.rg37_locus.contig),
        'liftedOverPos': lambda r: hl.or_missing(hl.is_defined(r.rg37_locus), r.rg37_locus.position),
    }

    SORTS = {
        XPOS: lambda r: [r.xpos],
    }

    @classmethod
    def load_globals(cls):
        ht_path = cls._get_table_path('annotations.ht')
        ht_globals = hl.eval(hl.read_table(ht_path).globals.select(*cls.GLOBALS))
        cls.LOADED_GLOBALS = {k: ht_globals[k] for k in cls.GLOBALS}

    @classmethod
    def _format_population_config(cls, pop_config):
        base_pop_config = {field.lower(): field for field in cls.POPULATION_KEYS}
        base_pop_config.update(pop_config)
        base_pop_config.pop('sort', None)
        return base_pop_config

    def annotation_fields(self, include_genotype_overrides=True):
        annotation_fields = {
            GENOTYPES_FIELD: lambda r: r.family_entries.flatmap(lambda x: x).filter(
                lambda gt: hl.is_defined(gt.individualGuid)
            ).group_by(lambda x: x.individualGuid).map_values(lambda x: x[0].select(
                'sampleId', 'sampleType', 'individualGuid', 'familyGuid',
                numAlt=hl.if_else(hl.is_defined(x[0].GT), x[0].GT.n_alt_alleles(), self.MISSING_NUM_ALT),
                **{k: x[0][field] for k, field in self.GENOTYPE_FIELDS.items()},
                **{_to_camel_case(k): v(x[0], k, r) for k, v in self.COMPUTED_GENOTYPE_FIELDS.items()
                   if include_genotype_overrides or k not in self.GENOTYPE_OVERRIDE_FIELDS},
            )),
            'populations': lambda r: hl.struct(**{
                population: self.population_expression(r, population) for population in self.POPULATIONS.keys()
            }),
            'predictions': lambda r: hl.struct(**{
                prediction: self._format_enum(r[path.source], path.field, self._enums[path.source][path.field])
                if self._enums.get(path.source, {}).get(path.field) else path.format(r[path.source][path.field])
                for prediction, path in self.PREDICTION_FIELDS_CONFIG.items()
            }),
        }
        annotation_fields.update(self.BASE_ANNOTATION_FIELDS)
        annotation_fields.update(self.LIFTOVER_ANNOTATION_FIELDS)
        annotation_fields.update(self._additional_annotation_fields())

        prediction_fields = {path.source for path in self.PREDICTION_FIELDS_CONFIG.values()}
        annotation_fields.update([
            self._format_enum_response(k, enum) for k, enum in self._enums.items()
            if enum and k not in prediction_fields
        ])

        return annotation_fields

    def _additional_annotation_fields(self):
        return {}

    def population_expression(self, r, population):
        pop_config = self._format_population_config(self.POPULATIONS[population])
        pop_field = self.POPULATION_FIELDS.get(population, population)
        return hl.struct(**{
            response_key: hl.or_else(r[pop_field][field], '' if response_key == 'id' else 0)
            for response_key, field in pop_config.items() if field is not None
        })

    def _get_enum_lookup(self, field, subfield):
        enum_field = self._enums.get(field, {})
        if subfield:
            enum_field = enum_field.get(subfield)
        if enum_field is None:
            return None
        return {v: i for i, v in enumerate(enum_field)}

    def _get_enum_terms_ids(self, field, subfield, terms):
        enum = self._get_enum_lookup(field, subfield)
        return {enum[t] for t in terms if enum.get(t) is not None}

    def _format_enum_response(self, k, enum):
        enum_config = self.ENUM_ANNOTATION_FIELDS.get(k, {})
        value = lambda r: self._format_enum(r, k, enum, ht_globals=self._globals, **enum_config)
        return enum_config.get('response_key', _to_camel_case(k)), value

    @classmethod
    def _format_enum(cls, r, field, enum, empty_array=False, format_array_values=None, **kwargs):
        if hasattr(r, f'{field}_id'):
            return hl.array(enum)[r[f'{field}_id']]

        value = r[field]
        if hasattr(value, 'map'):
            if empty_array:
                value = hl.or_else(value, hl.empty_array(value.dtype.element_type))
            value = value.map(lambda x: cls._enum_field(field, x, enum, **kwargs))
            if format_array_values:
                value = format_array_values(value, r)
            return value

        return cls._enum_field(field, value, enum, **kwargs)

    @staticmethod
    def _enum_field(field_name, value, enum, ht_globals=None, annotate_value=None, format_value=None, drop_fields=None, enum_keys=None, include_version=False, **kwargs):
        annotations = {}
        drop = [] + (drop_fields or [])
        value_keys = value.keys()
        for field in (enum_keys or enum.keys()):
            field_enum = enum[field]
            is_array = f'{field}_ids' in value_keys
            value_field = f"{field}_id{'s' if is_array else ''}"
            drop.append(value_field)

            enum_array = hl.array(field_enum)
            if is_array:
                annotations[f'{field}s'] = value[value_field].map(lambda v: enum_array[v])
            else:
                annotations[field] = enum_array[value[value_field]]

        if include_version:
            annotations['version'] = ht_globals['versions'][field_name]

        value = value.annotate(**annotations)
        if annotate_value:
            annotations = annotate_value(value, enum)
            value = value.annotate(**annotations)
        value = value.drop(*drop)

        if format_value:
            value = format_value(value)

        return value

    def __init__(self, sample_data, sort=XPOS, sort_metadata=None, num_results=100, inheritance_mode=None,
                 override_comp_het_alt=False, **kwargs):
        self.unfiltered_comp_het_ht = None
        self._sort = sort
        self._sort_metadata = sort_metadata
        self._num_results = num_results
        self._override_comp_het_alt = override_comp_het_alt
        self._ht = None
        self._comp_het_ht = None
        self._inheritance_mode = inheritance_mode
        self._has_secondary_annotations = False
        self._is_multi_data_type_comp_het = False
        self.max_unaffected_samples = None
        self._load_table_kwargs = {}
        self.entry_samples_by_family_guid = {}

        if sample_data:
            self._load_filtered_table(sample_data, **kwargs)

    @property
    def _has_comp_het_search(self):
        return self._inheritance_mode in {RECESSIVE, COMPOUND_HET}

    @property
    def _globals(self):
        return self.LOADED_GLOBALS

    @property
    def _enums(self):
        return self._globals['enums']

    def _load_filtered_table(self, sample_data, intervals=None, annotations=None, annotations_secondary=None, **kwargs):
        parsed_intervals = self._parse_intervals(intervals, **kwargs)
        parsed_annotations = self._parse_annotations(annotations, annotations_secondary, **kwargs)
        self.import_filtered_table(
            *self._parse_sample_data(sample_data), parsed_intervals=parsed_intervals, parsed_annotations=parsed_annotations, **kwargs)

    @classmethod
    def _get_table_path(cls, path, use_ssd_dir=False):
        return f'{SSD_DATASETS_DIR if use_ssd_dir else DATASETS_DIR}/{cls.GENOME_VERSION}/{cls.DATA_TYPE}/{path}'

    def _read_table(self, path, drop_globals=None, use_ssd_dir=False, skip_missing_field=None):
        table_path = self._get_table_path(path, use_ssd_dir=use_ssd_dir)
        if 'variant_ht' in self._load_table_kwargs:
            ht = self._query_table_annotations(self._load_table_kwargs['variant_ht'], table_path)
            if self._should_skip_ht(ht, skip_missing_field):
                return None
            ht_globals = hl.read_table(table_path).globals
            if drop_globals:
                ht_globals = ht_globals.drop(*drop_globals)
            return ht.annotate_globals(**hl.eval(ht_globals))

        ht = hl.read_table(table_path, **self._load_table_kwargs)
        return None if self._should_skip_ht(ht, skip_missing_field) else ht

    @staticmethod
    def _should_skip_ht(ht, skip_missing_field):
        return skip_missing_field and not ht.any(hl.is_defined(ht[skip_missing_field]))

    @staticmethod
    def _query_table_annotations(ht, query_table_path):
        query_result = hl.query_table(query_table_path, ht.key).first().drop(*ht.key)
        return ht.annotate(**query_result)

    def _parse_sample_data(self, sample_data):
        families = set()
        project_samples = defaultdict(lambda: defaultdict(list))
        for s in sample_data:
            families.add(s['family_guid'])
            project_samples[s['project_guid']][s['family_guid']].append(s)

        num_families = len(families)
        logger.info(f'Loading {self.DATA_TYPE} data for {num_families} families in {len(project_samples)} projects')
        return project_samples, num_families

    def _load_filtered_project_hts(self, project_samples, skip_all_missing=False, **kwargs):
        filtered_project_hts = []
        exception_messages = set()
        for i, (project_guid, project_sample_data) in enumerate(project_samples.items()):
            project_ht = self._read_table(
                f'projects/{project_guid}.ht',
                use_ssd_dir=True,
                skip_missing_field='family_entries' if skip_all_missing or i > 0 else None,
            )
            if project_ht is None:
                continue
            try:
                filtered_project_hts.append(
                    (*self._filter_entries_table(project_ht, project_sample_data, **kwargs), len(project_sample_data))
                )
            except HTTPBadRequest as e:
                exception_messages.add(e.reason)

        if exception_messages:
            raise HTTPBadRequest(reason='; '.join(exception_messages))

        if len(project_samples) > len(filtered_project_hts):
            logger.info(f'Found {len(filtered_project_hts)} {self.DATA_TYPE} projects with matched entries')
        return filtered_project_hts

    def import_filtered_table(self, project_samples, num_families, intervals=None, **kwargs):
        if num_families == 1:
            family_sample_data = list(project_samples.values())[0]
            family_guid = list(family_sample_data.keys())[0]
            family_ht = self._read_table(f'families/{family_guid}.ht', use_ssd_dir=True)
            family_ht = family_ht.transmute(family_entries=[family_ht.entries])
            family_ht = family_ht.annotate_globals(
                family_guids=[family_guid], family_samples={family_guid: family_ht.sample_ids},
            )
            families_ht, comp_het_families_ht = self._filter_entries_table(family_ht, family_sample_data, **kwargs)
        else:
            filtered_project_hts = self._load_filtered_project_hts(project_samples, **kwargs)
            families_ht, comp_het_families_ht, num_families = filtered_project_hts[0]
            main_ht = comp_het_families_ht if families_ht is None else families_ht
            entry_type = main_ht.family_entries.dtype.element_type
            for project_ht, comp_het_project_ht, num_project_families in filtered_project_hts[1:]:
                if families_ht is not None:
                    families_ht = self._add_project_ht(families_ht, project_ht, default=hl.empty_array(entry_type))
                if comp_het_families_ht is not None:
                    comp_het_families_ht = self._add_project_ht(
                        comp_het_families_ht, comp_het_project_ht,
                        default=hl.range(num_families).map(lambda i: hl.missing(entry_type)),
                        default_1=hl.range(num_project_families).map(lambda i: hl.missing(entry_type)),
                    )
                num_families += num_project_families

        if comp_het_families_ht is not None:
            comp_het_ht = self._query_table_annotations(comp_het_families_ht, self._get_table_path('annotations.ht'))
            self._comp_het_ht = self._filter_annotated_table(comp_het_ht, is_comp_het=True, **kwargs)
            self._comp_het_ht = self._filter_compound_hets()

        if families_ht is not None:
            ht = self._query_table_annotations(families_ht, self._get_table_path('annotations.ht'))
            self._ht = self._filter_annotated_table(ht, **kwargs)

    def _add_project_ht(self, families_ht, project_ht, default, default_1=None):
        if default_1 is None:
            default_1 = default

        families_ht = families_ht.join(project_ht, how='outer')
        families_ht = families_ht.select_globals(
            family_guids=families_ht.family_guids.extend(families_ht.family_guids_1)
        )
        return families_ht.select(
            filters=families_ht.filters.union(families_ht.filters_1),
            family_entries=hl.bind(
                lambda a1, a2: a1.extend(a2),
                hl.or_else(families_ht.family_entries, default),
                hl.or_else(families_ht.family_entries_1, default_1),
            ),
        )

    def _filter_entries_table(self, ht, sample_data, inheritance_filter=None, quality_filter=None, **kwargs):
        if not self._load_table_kwargs:
            ht = self._prefilter_entries_table(ht, **kwargs)

        ht, sorted_family_sample_data = self._add_entry_sample_families(ht, sample_data)

        quality_filter = quality_filter or {}
        if quality_filter.get('vcf_filter'):
            ht = self._filter_vcf_filters(ht)

        passes_quality_filter = self._get_family_passes_quality_filter(quality_filter, ht=ht, **kwargs)
        if passes_quality_filter is not None:
            ht = ht.annotate(family_entries=ht.family_entries.map(
                lambda entries: hl.or_missing(passes_quality_filter(entries), entries)
            ))
            ht = ht.filter(ht.family_entries.any(hl.is_defined))

        ht, ch_ht = self._filter_inheritance(
            ht, inheritance_filter, sorted_family_sample_data,
        )

        return ht, ch_ht

    def _add_entry_sample_families(self, ht, sample_data):
        ht_globals = hl.eval(ht.globals)

        missing_samples = set()
        family_sample_index_data = []
        family_guids = sorted(sample_data.keys())
        for family_guid in family_guids:
            samples = sample_data[family_guid]
            ht_family_samples = ht_globals.family_samples[family_guid]
            missing_family_samples = [s['sample_id'] for s in samples if s['sample_id'] not in ht_family_samples]
            if missing_family_samples:
                missing_samples.update(missing_family_samples)
            else:
                sample_index_data = [
                    (ht_family_samples.index(s['sample_id']), self._sample_entry_data(s, family_guid, ht_globals))
                    for s in samples
                ]
                family_sample_index_data.append(
                    (ht_globals.family_guids.index(family_guid), sample_index_data)
                )
                self.entry_samples_by_family_guid[family_guid] = [s['sampleId'] for _, s in sample_index_data]

        if missing_samples:
            raise HTTPBadRequest(
                reason=f'The following samples are available in seqr but missing the loaded data: {", ".join(sorted(missing_samples))}'
            )

        sorted_family_sample_data = [[sample for _, sample in samples] for _, samples in family_sample_index_data]
        family_sample_index_data = hl.array(family_sample_index_data)

        ht = ht.annotate_globals(family_guids=family_guids)

        ht = ht.transmute(family_entries=family_sample_index_data.map(lambda family_tuple: family_tuple[1].map(
            lambda sample_tuple: ht.family_entries[family_tuple[0]][sample_tuple[0]].annotate(**hl.struct(**sample_tuple[1]))
        )))

        return ht, sorted_family_sample_data

    @classmethod
    def _sample_entry_data(cls, sample, family_guid, ht_globals):
        return dict(
            sampleId=sample['sample_id'],
            sampleType=cls._get_sample_type(ht_globals),
            individualGuid=sample['individual_guid'],
            familyGuid=family_guid,
            affected_id=AFFECTED_ID_MAP.get(sample['affected']),
            is_male='sex' in sample and sample['sex'] == MALE,
        )

    @classmethod
    def _get_sample_type(cls, ht_globals):
        return ht_globals.sample_type

    def _filter_inheritance(self, ht, inheritance_filter, sorted_family_sample_data):
        any_valid_entry = lambda x: self.GENOTYPE_QUERY_MAP[HAS_ALT](x.GT)

        is_any_affected = self._inheritance_mode == ANY_AFFECTED
        if is_any_affected:
            prev_any_valid_entry = any_valid_entry
            any_valid_entry = lambda x: prev_any_valid_entry(x) & (x.affected_id == AFFECTED_ID)

        ht = ht.annotate(family_entries=ht.family_entries.map(
            lambda entries: hl.or_missing(entries.any(any_valid_entry), entries))
        )

        comp_het_ht = None
        if self._has_comp_het_search:
            comp_het_ht = self._filter_families_inheritance(
                ht, COMPOUND_HET, inheritance_filter, sorted_family_sample_data,
            )

        if is_any_affected or not (inheritance_filter or self._inheritance_mode):
            # No sample-specific inheritance filtering needed
            sorted_family_sample_data = []

        ht = None if self._inheritance_mode == COMPOUND_HET else self._filter_families_inheritance(
            ht, self._inheritance_mode, inheritance_filter, sorted_family_sample_data,
        )

        return ht, comp_het_ht

    def _filter_families_inheritance(self, ht, inheritance_mode, inheritance_filter, sorted_family_sample_data):
        individual_genotype_filter = (inheritance_filter or {}).get('genotype')

        entry_indices_by_gt = defaultdict(lambda: defaultdict(list))
        for family_index, samples in enumerate(sorted_family_sample_data):
            for sample_index, s in enumerate(samples):
                genotype = individual_genotype_filter.get(s['individualGuid']) \
                    if individual_genotype_filter else INHERITANCE_FILTERS[inheritance_mode].get(s['affected_id'])
                if inheritance_mode == X_LINKED_RECESSIVE and s['affected_id'] == UNAFFECTED_ID and s['is_male']:
                    genotype = REF_REF
                if genotype == COMP_HET_ALT and self._override_comp_het_alt:
                    genotype = HAS_ALT
                if genotype:
                    entry_indices_by_gt[genotype][family_index].append(sample_index)

        min_unaffected = None
        if inheritance_mode == COMPOUND_HET:
            family_unaffected_counts = [
                len(i) for i in entry_indices_by_gt[INHERITANCE_FILTERS[COMPOUND_HET][UNAFFECTED_ID]].values()
            ]
            self.max_unaffected_samples = max(family_unaffected_counts) if family_unaffected_counts else 0
            if self.max_unaffected_samples > 1:
                min_unaffected = min(family_unaffected_counts)

        for genotype, entry_indices in entry_indices_by_gt.items():
            if not entry_indices:
                continue
            entry_indices = hl.dict(entry_indices)
            ht = ht.annotate(family_entries=hl.enumerate(ht.family_entries).map(
                lambda x: self._valid_genotype_family_entries(x[1], entry_indices.get(x[0]), genotype, min_unaffected)
            ))

        return ht.filter(ht.family_entries.any(hl.is_defined)).select_globals('family_guids')

    @classmethod
    def _valid_genotype_family_entries(cls, entries, gentoype_entry_indices, genotype, min_unaffected):
        is_valid = hl.is_missing(gentoype_entry_indices) | gentoype_entry_indices.all(
            lambda i: cls.GENOTYPE_QUERY_MAP[genotype](entries[i].GT)
        )
        if min_unaffected is not None and genotype == HAS_REF:
            unaffected_filter = gentoype_entry_indices.any(
                lambda i: cls.GENOTYPE_QUERY_MAP[REF_REF](entries[i].GT)
            )
            if min_unaffected < 2:
                unaffected_filter |= gentoype_entry_indices.size() < 2
            is_valid &= unaffected_filter
        return hl.or_missing(is_valid, entries)

    def _get_family_passes_quality_filter(self, quality_filter, **kwargs):
        affected_only = quality_filter.get('affected_only')
        passes_quality_filters = []
        for filter_k, value in quality_filter.items():
            genotype_key = filter_k.replace('min_', '')
            field = self.GENOTYPE_QUERY_FIELDS.get(genotype_key, self.GENOTYPE_FIELDS.get(genotype_key))
            if field and value:
                passes_quality_filters.append(self._get_genotype_passes_quality_field(field, value, affected_only))

        if not passes_quality_filters:
            return None

        return lambda entries: entries.all(lambda gt: hl.all([f(gt) for f in passes_quality_filters]))

    @classmethod
    def _get_genotype_passes_quality_field(cls, field, value, affected_only):
        field_config = cls.QUALITY_FILTER_FORMAT.get(field) or QualityFilterFormat()
        if field_config.scale:
            value = value / field_config.scale

        def passes_quality_field(gt):
            is_valid = (gt[field] >= value) | hl.is_missing(gt[field])
            if field_config.override:
                is_valid |= field_config.override(gt)
            if affected_only:
                is_valid |= gt.affected_id != AFFECTED_ID
            return is_valid

        return passes_quality_field

    @staticmethod
    def _filter_vcf_filters(ht):
        return ht.filter(hl.is_missing(ht.filters) | (ht.filters.length() < 1))

    def _parse_variant_keys(self, variant_keys=None, **kwargs):
        return [hl.struct(**{self.KEY_FIELD[0]: key}) for key in (variant_keys or [])]

    def _prefilter_entries_table(self, ht, **kwargs):
        return ht

    def _filter_annotated_table(self, ht, gene_ids=None, rs_ids=None, frequencies=None, in_silico=None, pathogenicity=None,
                                parsed_annotations=None, is_comp_het=False, **kwargs):
        if gene_ids:
            ht = self._filter_by_gene_ids(ht, gene_ids)

        if rs_ids:
            ht = self._filter_rs_ids(ht, rs_ids)

        ht = self._filter_by_frequency(ht, frequencies, pathogenicity)

        ht = self._filter_by_in_silico(ht, in_silico)

        return self._filter_by_annotations(ht, is_comp_het, **(parsed_annotations or {}))

    def _filter_by_gene_ids(self, ht, gene_ids):
        gene_ids = hl.set(gene_ids)
        ht = ht.annotate(
            gene_transcripts=ht[self.TRANSCRIPTS_FIELD].filter(lambda t: gene_ids.contains(t.gene_id))
        )
        return ht.filter(hl.is_defined(ht.gene_transcripts.first()))

    def _filter_rs_ids(self, ht, rs_ids):
        rs_id_set = hl.set(rs_ids)
        return ht.filter(rs_id_set.contains(ht.rsid))

    def _parse_intervals(self, intervals, **kwargs):
        parsed_variant_keys = self._parse_variant_keys(**kwargs)
        if parsed_variant_keys:
            self._load_table_kwargs['variant_ht'] = hl.Table.parallelize(parsed_variant_keys).key_by(*self.KEY_FIELD)
            return intervals

        is_x_linked = self._inheritance_mode == X_LINKED_RECESSIVE
        if not (intervals or is_x_linked):
            return intervals

        raw_intervals = intervals
        if self._should_add_chr_prefix():
            intervals = [
                f'[chr{interval.replace("[", "")}' if interval.startswith('[') else f'chr{interval}'
                for interval in (intervals or [])
            ]

        if is_x_linked:
            reference_genome = hl.get_reference(self.GENOME_VERSION)
            intervals = (intervals or []) + [reference_genome.x_contigs[0]]

        parsed_intervals = [
            hl.eval(hl.parse_locus_interval(interval, reference_genome=self.GENOME_VERSION, invalid_missing=True))
            for interval in intervals
        ]
        invalid_intervals = [raw_intervals[i] for i, interval in enumerate(parsed_intervals) if interval is None]
        if invalid_intervals:
            raise HTTPBadRequest(reason=f'Invalid intervals: {", ".join(invalid_intervals)}')

        return parsed_intervals

    def _should_add_chr_prefix(self):
        return True

    def _filter_by_frequency(self, ht, frequencies, pathogenicity):
        frequencies = {k: v for k, v in (frequencies or {}).items() if k in self.POPULATIONS}
        if not frequencies:
            return ht

        path_override_filter = self._frequency_override_filter(ht, pathogenicity)
        filters = []
        for pop, freqs in sorted(frequencies.items()):
            pop_filters = []
            pop_expr = ht[self.POPULATION_FIELDS.get(pop, pop)]
            pop_config = self._format_population_config(self.POPULATIONS[pop])
            if freqs.get('af') is not None:
                af_field = pop_config.get('filter_af') or pop_config['af']
                pop_filter = pop_expr[af_field] <= freqs['af']
                if path_override_filter is not None and freqs['af'] < PATH_FREQ_OVERRIDE_CUTOFF:
                    pop_filter |= path_override_filter & (pop_expr[af_field] <= PATH_FREQ_OVERRIDE_CUTOFF)
                pop_filters.append(pop_filter)
            elif freqs.get('ac') is not None:
                ac_field = pop_config['ac']
                if ac_field:
                    pop_filters.append(pop_expr[ac_field] <= freqs['ac'])

            if freqs.get('hh') is not None:
                hom_field = pop_config['hom']
                hemi_field = pop_config['hemi']
                if hom_field:
                    pop_filters.append(pop_expr[hom_field] <= freqs['hh'])
                if hemi_field:
                    pop_filters.append(pop_expr[hemi_field] <= freqs['hh'])

            if pop_filters:
                filters.append(hl.is_missing(pop_expr) | hl.all(pop_filters))

        if filters:
            ht = ht.filter(hl.all(filters))
        return ht

    def _frequency_override_filter(self, ht, pathogenicity):
        return None

    def _filter_by_in_silico(self, ht, in_silico_filters):
        in_silico_filters = in_silico_filters or {}
        require_score = in_silico_filters.get('requireScore', False)
        in_silico_filters = {k: v for k, v in in_silico_filters.items() if k in self.PREDICTION_FIELDS_CONFIG and v}
        if not in_silico_filters:
            return ht

        in_silico_qs = []
        missing_qs = []
        for in_silico, value in in_silico_filters.items():
            score_filter, ht_value = self._get_in_silico_filter(ht, in_silico, value)
            in_silico_qs.append(score_filter)
            if not require_score:
                missing_qs.append(hl.is_missing(ht_value))

        if missing_qs:
            in_silico_qs.append(hl.all(missing_qs))

        return ht.filter(hl.any(in_silico_qs))

    def _get_in_silico_filter(self, ht, in_silico, value):
        score_path = self.PREDICTION_FIELDS_CONFIG[in_silico]
        enum_lookup = self._get_enum_lookup(*score_path[:2])
        if enum_lookup is not None:
            ht_value = ht[score_path.source][f'{score_path.field}_id']
            score_filter = ht_value == enum_lookup[value]
        else:
            ht_value = ht[score_path.source][score_path.field]
            score_filter = ht_value >= float(value)

        return score_filter, ht_value

    def _parse_annotations(self, annotations, annotations_secondary, **kwargs):
        annotations = annotations or {}
        allowed_consequence_ids = self._get_allowed_consequence_ids(annotations)
        annotation_overrides = self._get_annotation_override_fields(annotations, **kwargs)

        parsed_annotations = {}
        if self._has_comp_het_search and annotations_secondary:
            secondary_allowed_consequence_ids = self._get_allowed_consequence_ids(annotations_secondary)
            has_different_secondary = secondary_allowed_consequence_ids != allowed_consequence_ids
            has_data_type_primary_annotations = allowed_consequence_ids or annotation_overrides
            has_data_type_secondary_annotations = bool(secondary_allowed_consequence_ids)
            secondary_annotation_overrides = None
            if self.SECONDARY_ANNOTATION_OVERRIDE_FIELDS:
                secondary_annotation_overrides = self._get_annotation_override_fields(
                    annotations_secondary, override_fields=self.SECONDARY_ANNOTATION_OVERRIDE_FIELDS, **kwargs)
                has_data_type_secondary_annotations |= bool(secondary_annotation_overrides)
                has_different_secondary &= secondary_annotation_overrides != annotation_overrides

            if not has_data_type_primary_annotations:
                allowed_consequence_ids = secondary_allowed_consequence_ids
                annotation_overrides = secondary_annotation_overrides
                # Data type only has annotations for second hit, so there is no need for the homozygous recessive query
                self._inheritance_mode = COMPOUND_HET
            elif has_different_secondary:
                parsed_annotations.update({
                    'secondary_consequence_ids': secondary_allowed_consequence_ids,
                    'secondary_annotation_overrides': secondary_annotation_overrides,
                })
                self._has_secondary_annotations = True

            if not (has_data_type_primary_annotations and has_data_type_secondary_annotations):
                self._is_multi_data_type_comp_het = True

        parsed_annotations.update({
            'consequence_ids': allowed_consequence_ids,
            'annotation_overrides': annotation_overrides,
        })
        return parsed_annotations

    def _filter_by_annotations(self, ht, is_comp_het, consequence_ids=None, annotation_overrides=None,
                               secondary_consequence_ids=None, secondary_annotation_overrides=None, **kwargs):

        annotation_exprs = {}
        if consequence_ids:
            annotation_exprs[ALLOWED_TRANSCRIPTS] = self._get_allowed_transcripts(ht, consequence_ids)
            ht = ht.annotate(**annotation_exprs)
        annotation_filters = self._get_annotation_override_filters(ht, annotation_overrides or {})

        if not is_comp_het:
            if annotation_exprs:
                annotation_filters.append(self._has_allowed_transcript_filter(ht, ALLOWED_TRANSCRIPTS))
            if annotation_filters:
                ht = ht.filter(hl.any(annotation_filters))
            return ht

        if annotation_filters:
            annotation_exprs[HAS_ANNOTATION_OVERRIDE] = hl.any(annotation_filters)
        if secondary_annotation_overrides is not None:
            overrides = self._get_annotation_override_filters(ht, secondary_annotation_overrides)
            annotation_exprs[f'{HAS_ANNOTATION_OVERRIDE}_secondary'] = hl.any(overrides) if overrides else False
        secondary_allowed_transcripts_field = f'{ALLOWED_TRANSCRIPTS}_secondary'
        if secondary_consequence_ids:
            annotation_exprs[secondary_allowed_transcripts_field] = self._get_allowed_transcripts(ht, secondary_consequence_ids)

        filter_fields = list(annotation_exprs.keys())
        transcript_filter_fields = [ALLOWED_TRANSCRIPTS, secondary_allowed_transcripts_field]
        annotation_exprs.pop(ALLOWED_TRANSCRIPTS, None)
        if annotation_exprs:
            ht = ht.annotate(**annotation_exprs)

        all_filters = [
            self._has_allowed_transcript_filter(ht, field) if field in transcript_filter_fields else ht[field]
            for field in filter_fields
        ]
        return ht.filter(hl.any(all_filters))

    def _get_allowed_consequence_ids(self, annotations):
        allowed_consequences = {
            ann for field, anns in annotations.items()
            if anns and (field not in ANNOTATION_OVERRIDE_FIELDS) for ann in anns
        }
        return self._get_enum_terms_ids(self.TRANSCRIPTS_FIELD, self.TRANSCRIPT_CONSEQUENCE_FIELD, allowed_consequences)

    def _get_allowed_transcripts(self, ht, allowed_consequence_ids):
        transcript_filter = self._get_allowed_transcripts_filter(allowed_consequence_ids)
        return ht[self.TRANSCRIPTS_FIELD].filter(transcript_filter)

    @staticmethod
    def _get_allowed_transcripts_filter(allowed_consequence_ids):
        allowed_consequence_ids = hl.set(allowed_consequence_ids)
        return lambda gc: allowed_consequence_ids.contains(gc.major_consequence_id)

    def _get_annotation_override_fields(self, annotations, override_fields=None, **kwargs):
        override_fields = override_fields or self.ANNOTATION_OVERRIDE_FIELDS
        return {k: annotations[k] for k in override_fields if k in annotations}

    def _get_annotation_override_filters(self, ht, annotation_overrides):
        return []

    def _get_annotation_filters(self, ht, is_secondary=False):
        suffix = '_secondary' if is_secondary else ''
        annotation_filters = []

        allowed_transcripts_field = f'{ALLOWED_TRANSCRIPTS}{suffix}'
        if allowed_transcripts_field in ht.row:
            annotation_filters.append(self._has_allowed_transcript_filter(ht, allowed_transcripts_field))

        annotation_override_field = f'{HAS_ANNOTATION_OVERRIDE}{suffix}'
        if annotation_override_field in ht.row:
            annotation_filters.append(ht[annotation_override_field])
        elif HAS_ANNOTATION_OVERRIDE in ht.row:
            # For secondary annotations, if no secondary override is defined use the primary override
            annotation_filters.append(ht[HAS_ANNOTATION_OVERRIDE])

        return annotation_filters

    @staticmethod
    def _has_allowed_transcript_filter(ht, allowed_transcript_field):
        return hl.is_defined(ht[allowed_transcript_field].first())

    def _filter_compound_hets(self):
        # pylint: disable=pointless-string-statement
        ch_ht = self._comp_het_ht

        # Get possible pairs of variants within the same gene
        ch_ht = ch_ht.annotate(gene_ids=self._gene_ids_expr(ch_ht))
        ch_ht = ch_ht.explode(ch_ht.gene_ids)

        # Filter allowed transcripts to the grouped gene
        transcript_annotations = {
            k: ch_ht[k].filter(lambda t: t.gene_id == ch_ht.gene_ids)
            for k in [ALLOWED_TRANSCRIPTS, ALLOWED_SECONDARY_TRANSCRIPTS] if k in ch_ht.row
        }
        if transcript_annotations:
            ch_ht = ch_ht.annotate(**transcript_annotations)

        if transcript_annotations or self._has_secondary_annotations:
            primary_filters = self._get_annotation_filters(ch_ht)
            secondary_filters = self._get_annotation_filters(ch_ht, is_secondary=True) if self._has_secondary_annotations else []
            self.unfiltered_comp_het_ht = ch_ht.filter(hl.any(primary_filters + secondary_filters))
        else:
            self.unfiltered_comp_het_ht = ch_ht

        if self._is_multi_data_type_comp_het:
            # In cases where comp het pairs must have different data types, there are no single data type results
            return None

        if self._has_secondary_annotations:
            primary_variants = hl.agg.filter(hl.any(primary_filters), hl.agg.collect(ch_ht.row))
            row_agg = ch_ht.row
            if ALLOWED_TRANSCRIPTS in row_agg and ALLOWED_SECONDARY_TRANSCRIPTS in row_agg:
                # Ensure main transcripts are properly selected for primary/secondary annotations in variant pairs
                row_agg = row_agg.annotate(**{ALLOWED_TRANSCRIPTS: row_agg[ALLOWED_SECONDARY_TRANSCRIPTS]})
            secondary_variants = hl.agg.filter(hl.any(secondary_filters), hl.agg.collect(row_agg))
        else:
            if transcript_annotations:
                ch_ht = ch_ht.filter(hl.any(self._get_annotation_filters(ch_ht)))
            primary_variants = hl.agg.collect(ch_ht.row)
            secondary_variants = primary_variants

        ch_ht = ch_ht.group_by('gene_ids').aggregate(v1=primary_variants, v2=secondary_variants)

        # Compute all distinct variant pairs
        """ Assume a table with the following data
         gene_ids | v1     | v2
         A        | [1, 2] | [1, 2, 3]
         B        | [2]    | [2, 3]
        """
        key_expr = lambda v: v[self.KEY_FIELD[0]] if len(self.KEY_FIELD) == 1 else hl.tuple([v[k] for k in self.KEY_FIELD])
        ch_ht = ch_ht.annotate(
            v1_set=hl.set(ch_ht.v1.map(key_expr)),
            v2=ch_ht.v2.group_by(key_expr).map_values(lambda x: x[0]),
        )
        ch_ht = ch_ht.explode(ch_ht.v1)
        """ After annotating and exploding by v1:
         gene_ids | v1 | v2                          | v1_set 
         A        | 1  | {id_1: 1, id_2: 2, id_3: 3} | {id_1, id_2}
         A        | 2  | {id_2: 2, id_3: 3}          | {id_1, id_2}
         B        | 2  | {id_2: 2, id_3: 3}          | {id_2}
        """

        v1_key = key_expr(ch_ht.v1)
        ch_ht = ch_ht.annotate(v2=ch_ht.v2.items().filter(
            lambda x: ~ch_ht.v2.contains(v1_key) | ~ch_ht.v1_set.contains(x[0]) | (x[0] > v1_key)
        ))
        """ After filtering v2:
         gene_ids | v1 | v2                     | v1_set 
         A        | 1  | [(id_2, 2), (id_3, 3)] | {id_1, id_2}
         A        | 2  | [(id_3, 3)]            | {id_1, id_2}
         B        | 2  | [(id_3, 3)]            | {id_2}
        """

        ch_ht = ch_ht.group_by('v1').aggregate(
            comp_het_gene_ids=hl.agg.collect_as_set(ch_ht.gene_ids),
            v2_items=hl.agg.collect(ch_ht.v2).flatmap(lambda x: x),
        )
        ch_ht = ch_ht.annotate(v2=hl.dict(ch_ht.v2_items).values())
        """ After grouping by v1:
         v1 | v2     | comp_het_gene_ids
         1  | [2, 3] | {A}
         2  | [3]    | {A, B}             
        """

        ch_ht = ch_ht.explode(ch_ht.v2)._key_by_assert_sorted()
        """ After exploding by v2:
         v1 | v2 | comp_het_gene_ids
         1  | 2  | {A}
         1  | 3  | {A}
         2  | 3  | {A, B}             
        """

        ch_ht = self._filter_grouped_compound_hets(ch_ht)

        # Return pairs formatted as lists
        return ch_ht.select(**{GROUPED_VARIANTS_FIELD: hl.array([ch_ht.v1, ch_ht.v2])})

    def _filter_grouped_compound_hets(self, ch_ht):
        # Filter variant pairs for family and genotype
        ch_ht = ch_ht.annotate(valid_families=hl.enumerate(ch_ht.v1.family_entries).map(
            lambda x: self._is_valid_comp_het_family(ch_ht, x[1], ch_ht.v2.family_entries[x[0]])
        ))
        ch_ht = ch_ht.filter(ch_ht.valid_families.any(lambda x: x))
        ch_ht = ch_ht.select(**{k: self._annotated_comp_het_variant(ch_ht, k) for k in ['v1', 'v2']})

        return ch_ht

    @staticmethod
    def _annotated_comp_het_variant(ch_ht, field):
        variant = ch_ht[field]
        return variant.annotate(
            comp_het_gene_ids=ch_ht.comp_het_gene_ids,
            family_entries=hl.enumerate(ch_ht.valid_families).filter(
                lambda x: x[1]).map(lambda x: variant.family_entries[x[0]]),
        )

    @classmethod
    def _gene_ids_expr(cls, ht):
        return hl.set(ht[cls.TRANSCRIPTS_FIELD].map(lambda t: t.gene_id))

    def _is_valid_comp_het_family(self, ch_ht, entries_1, entries_2):
        family_filters = [hl.is_defined(entries_1), hl.is_defined(entries_2)]
        if self.max_unaffected_samples > 0:
            family_filters.append(hl.enumerate(entries_1).all(lambda x: hl.any([
                (x[1].affected_id != UNAFFECTED_ID), *self._comp_het_entry_has_ref(x[1].GT, entries_2[x[0]].GT),
            ])))
        if self._override_comp_het_alt:
            family_filters.append(entries_1.extend(entries_2).all(lambda x: ~self.GENOTYPE_QUERY_MAP[ALT_ALT](x.GT)))
        return hl.all(family_filters)

    def _comp_het_entry_has_ref(self, gt1, gt2):
        return [self.GENOTYPE_QUERY_MAP[REF_REF](gt1), self.GENOTYPE_QUERY_MAP[REF_REF](gt2)]

    def _format_comp_het_results(self, ch_ht, annotation_fields):
        formatted_grouped_variants = ch_ht[GROUPED_VARIANTS_FIELD].map(
            lambda v: self._format_results(v, annotation_fields=annotation_fields)
        )
        ch_ht = ch_ht.annotate(**{GROUPED_VARIANTS_FIELD: hl.sorted(formatted_grouped_variants, key=lambda x: x._sort)})
        return ch_ht.annotate(_sort=ch_ht[GROUPED_VARIANTS_FIELD][0]._sort)

    def _format_results(self, ht, annotation_fields=None, **kwargs):
        if annotation_fields is None:
            annotation_fields = self.annotation_fields()
        annotations = {k: v(ht) for k, v in annotation_fields.items()}
        annotations.update({
            '_sort': self._sort_order(ht),
            'genomeVersion': self.GENOME_VERSION.replace('GRCh', ''),
        })
        results = ht.annotate(**annotations)
        return results.select(*self.CORE_FIELDS, *list(annotations.keys()))

    def format_search_ht(self):
        ch_ht = None
        annotation_fields = self.annotation_fields()
        if self._comp_het_ht:
            ch_ht = self._format_comp_het_results(self._comp_het_ht, annotation_fields)

        if self._ht:
            ht = self._format_results(self._ht.key_by(), annotation_fields=annotation_fields)
            if ch_ht:
                ht = ht.union(ch_ht, unify=True)
        else:
            ht = ch_ht
        return ht

    def search(self):
        ht = self.format_search_ht()

        (total_results, collected) = ht.aggregate((hl.agg.count(), hl.agg.take(ht.row, self._num_results, ordering=ht._sort)))
        logger.info(f'Total hits: {total_results}. Fetched: {self._num_results}')

        return self._format_collected_rows(collected), total_results

    def _format_collected_rows(self, collected):
        if self._has_comp_het_search:
            return [row.get(GROUPED_VARIANTS_FIELD) or row.drop(GROUPED_VARIANTS_FIELD) for row in collected]
        return collected

    def _sort_order(self, ht):
        sort_expressions = self._get_sort_expressions(ht, XPOS)
        if self._sort != XPOS:
            sort_expressions = self._get_sort_expressions(ht, self._sort) + sort_expressions
        return sort_expressions

    def _get_sort_expressions(self, ht, sort):
        if sort in self.SORTS:
            return self.SORTS[sort](ht)

        if sort in self.PREDICTION_FIELDS_CONFIG:
            prediction_path = self.PREDICTION_FIELDS_CONFIG[sort]
            return [hl.or_else(-hl.float64(ht[prediction_path.source][prediction_path.field]), 0)]

        if sort == OMIM_SORT:
            return self._omim_sort(ht, hl.set(set(self._sort_metadata)))

        if self._sort_metadata:
            return self._gene_rank_sort(ht, hl.dict(self._sort_metadata))

        sort_field = next((field for field, config in self.POPULATIONS.items() if config.get('sort') == sort), None)
        if sort_field:
            return [hl.float64(self.population_expression(ht, sort_field).af)]

        return []

    @classmethod
    def _omim_sort(cls, r, omim_gene_set):
        return [-cls._gene_ids_expr(r).intersection(omim_gene_set).size()]

    @classmethod
    def _gene_rank_sort(cls, r, gene_ranks):
        return [hl.min(cls._gene_ids_expr(r).map(gene_ranks.get))]

    @classmethod
    def _gene_count_selects(cls):
        return {
            'gene_ids': cls._gene_ids_expr,
            'families': cls.BASE_ANNOTATION_FIELDS[FAMILY_GUID_FIELD],
        }

    def format_gene_count_hts(self):
        hts = []
        selects = self._gene_count_selects()
        if self._comp_het_ht:
            ch_ht = self._comp_het_ht.explode(self._comp_het_ht[GROUPED_VARIANTS_FIELD])
            hts.append(ch_ht.select(**{k: v(ch_ht[GROUPED_VARIANTS_FIELD]) for k, v in selects.items()}))
        if self._ht:
            hts.append(self._ht.select(**{k: v(self._ht) for k, v in selects.items()}))
        return hts

    def gene_counts(self):
        hts = self.format_gene_count_hts()
        ht = hts[0].key_by()
        for sub_ht in hts[1:]:
            ht = ht.union(sub_ht.key_by(), unify=True)

        ht = ht.explode('gene_ids').explode('families')
        return ht.aggregate(hl.agg.group_by(
            ht.gene_ids, hl.struct(total=hl.agg.count(), families=hl.agg.counter(ht.families))
        ))

    def lookup_variant(self, variant_id, sample_data=None):
        self._parse_intervals(intervals=None, variant_ids=[variant_id], variant_keys=[variant_id])
        ht = self._read_table('annotations.ht', drop_globals=['paths', 'versions'])
        ht = ht.filter(hl.is_defined(ht[XPOS]))

        annotation_fields = self.annotation_fields(include_genotype_overrides=False)
        entry_annotations = {k: annotation_fields[k] for k in [FAMILY_GUID_FIELD, GENOTYPES_FIELD]}
        annotation_fields.update({
            FAMILY_GUID_FIELD: lambda ht: hl.empty_array(hl.tstr),
            GENOTYPES_FIELD: lambda ht: hl.empty_dict(hl.tstr, hl.tstr),
            'genotypeFilters': lambda ht: hl.str(''),
        })

        formatted = self._format_results(ht.key_by(), annotation_fields=annotation_fields, include_genotype_overrides=False)

        variants = formatted.aggregate(hl.agg.take(formatted.row, 1))
        if not variants:
            raise HTTPNotFound()
        variant = dict(variants[0])

        if sample_data:
            project_samples, _ = self._parse_sample_data(sample_data)
            for pht, _, _ in self._load_filtered_project_hts(project_samples, skip_all_missing=True):
                project_entries = pht.aggregate(hl.agg.take(hl.struct(**{k: v(pht) for k, v in entry_annotations.items()}), 1))
                variant[FAMILY_GUID_FIELD] += project_entries[0][FAMILY_GUID_FIELD]
                variant[GENOTYPES_FIELD].update(project_entries[0][GENOTYPES_FIELD])

        return variant
