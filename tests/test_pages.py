#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mock

from django.test import TestCase
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from feincms.module.page.models import Page
from feincms.content.richtext.models import RichTextContent


class TestPagesBase(TestCase):
    def setUp(self):
        u = User(username='test', is_active=True, is_staff=True, is_superuser=True)
        u.set_password('test')
        u.save()

        self.site_1 = Site.objects.all()[0]

    def login(self):
        self.assertTrue(self.client.login(username='test', password='test'))

    def create_page(self, title='Test page', parent='', **kwargs):
        dic = {
            'title': title,
            'slug': kwargs.get('slug', slugify(title)),
            'parent': parent,
            'template_key': 'internalpage',
            'publication_date_0': '2009-01-01',
            'publication_date_1': '00:00:00',
            'initial-publication_date_0': '2009-01-01',
            'initial-publication_date_1': '00:00:00',
            'language': 'en',
            'site': self.site_1.id,

            'rawcontent_set-TOTAL_FORMS': 0,
            'rawcontent_set-INITIAL_FORMS': 0,
            'rawcontent_set-MAX_NUM_FORMS': 10,
            }
        dic.update(kwargs)
        return self.client.post('/admin/page/page/add/', dic)


class TestMaxNavigationLevel(TestPagesBase):

    def test_max_3(self):
        self.login()

        with mock.patch('feincms_bounds.admin.django_settings') as dj_settings:
            dj_settings.FEINCMS_NAVIGATION_LEVEL = 3

            # creating pages in 3 levels
            parent = None
            for level in range(1, 4):
                # LEVEL `level`
                title = 'Test level %s' % level
                slug = 'test-page-levl%s' % level

                kwargs = {
                    'title': title, 'slug': slug
                }
                if parent:
                    kwargs['parent'] = parent.pk
                self.create_page(**kwargs)
                self.assertEqual(Page.objects.count(), level)
                parent = Page.objects.get(slug=slug)

            # LEVEL 4 => not allowed
            response = self.create_page(
                title='Test level 4', slug='test-page-levl4', parent=parent.pk
            )
            self.assertEqual(
                response.context_data['adminform'].form.errors,
                {'parent': [u'Only 3 levels allowed']}
            )

            # from nose.tools import set_trace; set_trace()
            self.assertEqual(Page.objects.count(), 3)
            self.assertRaises(Page.DoesNotExist, Page.objects.get, slug='test-page-levl4')

    def test_max_undefined(self):
        self.login()

        # creating pages in 10 levels
        parent = None
        for level in range(1, 11):
            # LEVEL `level`
            title = 'Test level %s' % level
            slug = 'test-page-levl%s' % level

            kwargs = {
                'title': title, 'slug': slug
            }
            if parent:
                kwargs['parent'] = parent.pk
            self.create_page(**kwargs)
            self.assertEqual(Page.objects.count(), level)
            parent = Page.objects.get(slug=slug)
