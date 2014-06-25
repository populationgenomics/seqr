from xbrowse_server.decorators import log_request
from xbrowse_server.base.models import Project, Family, Cohort
from xbrowse_server.base.utils import get_disease_association_json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings

from xbrowse import constants
from xbrowse import inheritance as x_inheritance
from xbrowse import variant_filters as x_variant_filters
from xbrowse import quality_filters as x_quality_filters
from xbrowse import utils as xbrowse_utils

import json


@login_required
@log_request('mendelian_variant_search')
def mendelian_variant_search(request, project_id, family_id):

    project = get_object_or_404(Project, project_id=project_id)
    family = get_object_or_404(Family, project=project, family_id=family_id)
    if not project.can_view(request.user):
        return HttpResponse('unauthorized')

    if not family.has_data('variation'):
        return render(request, 'analysis_unavailable.html', {
            'reason': 'This family does not have any variant data.'
        })

    return render(request, 'mendelian_variant_search.html', {
        'project': project, 
        'family': family,
        'family_genotype_filters_json': json.dumps(x_inheritance.get_genotype_filters(family.xfamily())),
        'project_options_json': project.get_options_json(),
    })

@login_required
@log_request('cohort_variant_search')
def cohort_variant_search(request, project_id, cohort_id):

    project = get_object_or_404(Project, project_id=project_id)
    cohort = get_object_or_404(Cohort, project=project, cohort_id=cohort_id)
    if not project.can_view(request.user):
        return HttpResponse('unauthorized')

    return render(request, 'cohort/cohort_variant_search.html', {
        'project': project,
        'cohort': cohort,
        'family_genotype_filters_json': json.dumps(x_inheritance.get_genotype_filters(cohort.xfamily())),
        'project_options_json': project.get_options_json(),
    })

@login_required
@log_request('cohort_gene_search')
def cohort_gene_search(request, project_id, cohort_id):

    project = get_object_or_404(Project, project_id=project_id)
    cohort = get_object_or_404(Cohort, project=project, cohort_id=cohort_id)
    if not project.can_view(request.user):
        return HttpResponse('unauthorized')

    return render(request, 'cohort/cohort_gene_search.html', {
        'project': project, 
        'cohort': cohort,
        'project_options_json': project.get_options_json(),
    })

