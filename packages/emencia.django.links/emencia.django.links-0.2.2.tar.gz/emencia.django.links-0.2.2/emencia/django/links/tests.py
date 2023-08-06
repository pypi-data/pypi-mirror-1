# -*- coding: utf-8 -*-
from datetime import date, timedelta
from django.test import TestCase
from django.db import IntegrityError
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.template import TemplateSyntaxError
from emencia.django.links.models import Link

class FakeRequest(object):
    LANGUAGE_CODE = 'en'

class LinksTest(TestCase):
    """
    Tests for emencia.django.links Application
    """

    #fixtures = ['test_data']

    def test_create_link(self):
        """
        Create some link
        """
        self.assertRaises(IntegrityError, Link.objects.create)
        data = {'title' : 'My link',
                'language' : 'en',
                'url' : 'http://www.emencia.fr',
                'site' : Site.objects.get_current(),
                }
        link = Link.objects.create(**data)
        link.save()
        linkbis = Link.objects.get(id=1)
        self.assertEqual(linkbis.title, 'My link')

    def test_published(self):
        data = {'title' : 'link1',
                'language' : 'en',
                'url' : 'http://www.emencia.fr',
                'site' : Site.objects.get_current(),
                 }

        link1 = Link.objects.create(**data)
        link1.save()
        link2 = Link.objects.create(**data)
        link2.title = 'link2'
        link2.save()
        link3 = Link.objects.create(**data)
        link3.title = 'link3'
        link3.save()
        link4 = Link.objects.create(**data)
        link4.title = 'link4'
        link4.save()
        link5 = Link.objects.create(**data)
        link5.title = 'link5'
        link5.save()
        self.assertEqual(len(Link.objects.all()), 5)
        self.assertEqual(len(Link.published.all()), 5)

        link2.publication_start = date.today() - timedelta(3)
        link2.publication_end = date.today() - timedelta(2)
        link2.save()

        link3.publication_start = date.today() + timedelta(2)
        link3.publication_end = date.today() + timedelta(3)
        link3.save()

        link4.visibility = False
        link4.save()

        self.assertEqual(len(Link.objects.all()), 5)
        self.assertEqual(len(Link.published.all()), 2)
        self.assertEqual(Link.published.all()[0].title, 'link5')
        self.assertEqual(Link.published.all()[1].title, 'link1')

        link5.site = Site.objects.create(domain='new.domain',
                                         name='new name')
        link5.save()
        self.assertEqual(len(Link.published.all()), 1)

    def test_view_create(self):
        """
        test the listing view of links filter by language
        """
        data = {'title' : 'My link',
                'language' : 'en',
                'url' : 'http://www.emencia.fr',
                'site' : Site.objects.get_current(),
                }
        link = Link.objects.create(**data)
        link.save()
        response = self.client.get(reverse('links_list'))
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'links/links_by_language.html')
        self.assertContains(response, '<title>Links</title>')
        self.assertContains(response, '<p><a href="http://www.emencia.fr">My link</a></p>')

    def test_get_latest_links_tag(self):
        """
        test the template tags get_latest_links
        """
        datas = ({'title' : 'My link',
                  'language' : 'en',
                  'site' : Site.objects.get_current(),
                  'url' : 'http://www.emencia.fr',},
                 {'title' : 'My link 2',
                  'language' : 'en',
                  'site' : Site.objects.get_current(),
                  'url' : 'http://www.emencia.fr',},
                 {'title' : 'Mon lien',
                  'language' : 'fr',
                  'site' : Site.objects.get_current(),
                  'url' : 'http://www.emencia.fr',},
                 {'title' : 'My link 3',
                  'language' : 'en',
                  'site' : Site.objects.get_current(),
                  'url' : 'http://www.emencia.fr',},
                )

        for data in datas:
            link = Link.objects.create(**data)
            link.save()

        t = Template("""
        {% load links_monitoring %}
        {% get_latest_links 2 as last_link %}
        {% for link in last_link %}
            <span>{{ link.title }}</span>
        {% endfor %}
        """)
        fake_request = FakeRequest()
        d = {'request' : fake_request}
        html = t.render(Context(d))
        self.assert_("<span>My link</span>" not in html)
        self.assert_("<span>My link 2</span>" in html)
        self.assert_("<span>Mon lien</span>" not in html)
        self.assert_("<span>My link 3</span>"  in html)

    def test_get_latest_links_tag_syntax(self):
        """
        test wrong syntax with the template tags get_latest_links
        """
        template ="""
        {% load links_monitoring %}
        {% get_latest_links 2 to last_link %}
        {% for link in last_link %}
            <span>{{ link.title }}</span>
        {% endfor %}
        """
        self.assertRaises(TemplateSyntaxError, Template, template)
        template ="""
        {% load links_monitoring %}
        {% get_latest_links %}
        {% for link in last_link %}
            <span>{{ link.title }}</span>
        {% endfor %}
        """
        self.assertRaises(TemplateSyntaxError, Template, template)
