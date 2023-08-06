# -*- coding: utf-8 -*-
"""Admin for emencia.django.links"""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from emencia.django.links.models import Category
from emencia.django.links.models import Link


class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'language', 'visibility')
    date_hierarchy = 'creation'
    list_filter = ('author', 'visibility', 'creation')
    search_fields = ('title', 'description', 'url')
    fieldsets = ((None, {'fields': ('title', 'description', 'url')}),
                 (_('Attributs'), {'fields': ('language', 'category',)}),
                 (_('Metadata'), {'fields': ('visibility', 'ordering',
                                             'publication_start', 'publication_end')}),
                 )

admin.site.register(Link, LinkAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Category, CategoryAdmin)
