import json
import logging
from django.contrib.auth.models import User

from seqr.models import SavedVariant, VariantSearchResults
from seqr.utils.es_utils import get_es_variants_by_ids, get_latest_samples_for_families, InvalidIndexException

from xbrowse_server.api.utils import add_extra_info_to_variants_project
from xbrowse_server.mall import get_reference
from xbrowse_server.base.models import Project as BaseProject
from xbrowse_server.base.lookups import get_variants_from_variant_tuples


def deprecated_get_or_create_saved_variant(xpos=None, ref=None, alt=None, family=None, project=None, **kwargs):
    if not project:
        project = family.project
    saved_variant, _ = SavedVariant.objects.get_or_create(
        xpos_start=xpos,
        xpos_end=xpos + len(ref) - 1,
        ref=ref,
        alt=alt,
        family=family,
        project=project,
    )
    if not saved_variant.saved_variant_json:
        try:
            saved_variants_json = _retrieve_saved_variants_json(project, [(xpos, ref, alt, family)], create_if_missing=True)
            if len(saved_variants_json):
                _update_saved_variant_json(saved_variant, saved_variants_json[0])
        except Exception as e:
            logging.error("Unable to retrieve variant annotations for %s (%s, %s, %s): %s" % (family, xpos, ref, alt, e))
    return saved_variant


def update_project_saved_variant_json(project, family_id=None):
    saved_variants = SavedVariant.objects.filter(project=project, family__isnull=False).select_related('family')
    if family_id:
        saved_variants = saved_variants.filter(family__family_id=family_id)

    saved_variants_map = {(v.xpos_start, v.ref, v.alt, v.family): v for v in saved_variants}
    variant_tuples = saved_variants_map.keys()
    saved_variants_map = {
        (xpos, ref, alt, family.guid): v for (xpos, ref, alt, family), v in saved_variants_map.items()
    }

    variants_json = _retrieve_saved_variants_json(project, variant_tuples)

    updated_saved_variant_guids = []
    for var in variants_json:
        for family_guid in var['familyGuids']:
            saved_variant = saved_variants_map[(var['xpos'], var['ref'], var['alt'], family_guid)]
            _update_saved_variant_json(saved_variant, var)
            updated_saved_variant_guids.append(saved_variant.guid)

    return updated_saved_variant_guids


def reset_cached_search_results(project):
    VariantSearchResults.objects.filter(families__project=project).distinct().update(
        es_index=None,
        results=None,
        total_results=None,
    )


def _retrieve_saved_variants_json(project, variant_tuples, create_if_missing=False):
    xpos_ref_alt_tuples = []
    xpos_ref_alt_family_tuples = []
    family_id_to_guid = {}
    for xpos, ref, alt, family in variant_tuples:
        xpos_ref_alt_tuples.append((xpos, ref, alt))
        xpos_ref_alt_family_tuples.append((xpos, ref, alt, family.family_id))
        family_id_to_guid[family.family_id] = family.guid

    samples = get_latest_samples_for_families(project.family_set.filter(guid__in=family_id_to_guid.values()))

    try:
        return get_es_variants_by_ids(samples, xpos_ref_alt_tuples)
    except InvalidIndexException:
        variants = _deprecated_retrieve_saved_variants_json(project, xpos_ref_alt_family_tuples, create_if_missing)
        for var in variants:
            var['familyGuids'] = [family_id_to_guid[var['extras']['family_id']]]
        return variants


def _deprecated_retrieve_saved_variants_json(project, variant_tuples, create_if_missing):
    project_id = project.deprecated_project_id
    xbrowse_project = BaseProject.objects.get(project_id=project_id)
    user = User.objects.filter(is_staff=True).first()  # HGMD annotations are only returned for staff users

    variants = get_variants_from_variant_tuples(xbrowse_project, variant_tuples, user=user)
    if not create_if_missing:
        variants = [var for var in variants if not var.get_extra('created_variant')]
    add_extra_info_to_variants_project(get_reference(), xbrowse_project, variants, add_populations=True)
    return [variant.toJSON() for variant in variants]


def _update_saved_variant_json(saved_variant, saved_variant_json):
    saved_variant.saved_variant_json = json.dumps(saved_variant_json)
    saved_variant.save()



