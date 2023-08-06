# -*- coding: utf-8 -*-
"""views for emencia.django.links"""
# Create your views here.
from django.views.generic import list_detail
from emencia.django.links.models import Link

def links_by_language(request):

    # Use the object_list view for the heavy lifting.
    language = request.LANGUAGE_CODE
    return list_detail.object_list(
        request,
        queryset = Link.published.filter(language=language),
        template_name = "links/links_by_language.html",
        template_object_name = "links",
    )
