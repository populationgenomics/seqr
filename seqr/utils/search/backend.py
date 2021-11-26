from typing import List, Dict, Optional
import abc

from seqr.utils.elasticsearch.utils import InvalidIndexException
from seqr.utils.search.expression import Expression
from seqr.utils.search.models import DatasetType
from seqr.utils.redis_utils import safe_redis_get_json, safe_redis_set_json


class Backend(abc.ABC):

    @abc.abstractmethod
    def search(self, expression: Expression):
        pass

    @abc.abstractmethod
    def get_genome_version_for_index_name(self, index_name: str) -> Optional[DatasetType]:
        """
        One of:
            GENOME_VERSION_GRCh37 = "37"
            GENOME_VERSION_GRCh38 = "38"
        """

    @abc.abstractmethod
    def get_dataset_type_for_index_name(self, index_name: str) -> Optional[str]:
        """
        One of `Sample.DATASET_TYPE_CHOICES`:
            DATASET_TYPE_VARIANT_CALLS = 'VARIANTS'
            DATASET_TYPE_SV_CALLS = 'SV'
        """
        pass

    @abc.abstractmethod
    def get_field_metadata_for_index_name(self, index_name: str) -> Dict[str, str]:
        # TODO: standardise the dataset types that come back
        # elasticsearch current returns:
        #   integer, double, keyword, float, nested, one, boolean, long
        pass


class ElasticsearchBackend(Backend):

    def __init__(self):
        self.client = None
        self.cached_metadata_for_index: Dict[str, any] = {}

    def get_field_metadata_for_index_name(self, index_name: str) -> Dict[str, str]:
        metadata = self._get_es_metadata_for_index_name(index_name)
        return metadata['fields']

    def get_genome_version_for_index_name(self, index_name: str) -> Optional[str]:
        metadata = self._get_es_metadata_for_index_name(index_name)
        return metadata['genomeVersion']

    def get_dataset_type_for_index_name(self, index_name: str) -> Optional[DatasetType]:
        metadata = self._get_es_metadata_for_index_name(index_name)
        dataset_type = metadata['genomeVersion']
        return DatasetType(dataset_type)

    def _get_es_metadata_for_index_name(self, index_name, use_redis_cache=False) -> Dict[str, any]:
        """
        TODO: enable use_redis_cache by default
        """

        if index_name in self.cached_metadata_for_index:
            return self.cached_metadata_for_index[index_name]

        index_metadata = {}

        cache_key = 'index_metadata__{}'.format(index_name)
        if use_redis_cache:
            # try pulling from the redis cache
            index_metadata = safe_redis_get_json(cache_key)

        if not index_metadata:
            # if the redis cache didn't work, get it from ES
            try:
                mappings = self.client.indices.get_mapping(index=index_name)
            except Exception as e:
                raise InvalidIndexException('{} - Error accessing index: {}'.format(
                    index_name, e.error if hasattr(e, 'error') else str(e)))
            for index_name, mapping in mappings.items():
                variant_mapping = mapping['mappings']
                index_metadata = variant_mapping.get('_meta', {})
                index_metadata['fields'] = {
                    field: field_props.get('type') for field, field_props in variant_mapping['properties'].items()
                }

            # if use_cache and include_fields:
            if use_redis_cache:
                # Only cache metadata with fields
                safe_redis_set_json(cache_key, index_metadata)

        self.cached_metadata_for_index[index_name] = index_metadata
        return index_metadata
