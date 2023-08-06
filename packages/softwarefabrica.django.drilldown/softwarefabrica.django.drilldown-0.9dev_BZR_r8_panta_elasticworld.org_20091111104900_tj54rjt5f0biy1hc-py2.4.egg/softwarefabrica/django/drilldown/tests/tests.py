# -*- coding: utf-8 -*-

import os
from django.db.models import Q
from django.test import TestCase

from softwarefabrica.django.drilldown.tests.models import *

import logging

class TestDrillDownView(TestCase):
    #fixtures = ['drilldown_test']

    def setUp(self):
        self.author_dante = Author(first_name = 'Dante', last_name='Alighieri',
                                   birth_date = '1265-06-01', death_date='1321-09-14')
        self.author_dante.save()

    def tearDown(self):
        pass

    #def test_has_perm(self):
    #    p_ev = Permission.has_perm(self.u_paul, Permission.UPDATE, self.s_world)
    #    self.assertTrue(p_ev.ok)
    #    self.assertEquals(p_ev.reason, Permission.objects.get(name = 'section_EDITORS_u_d'))
    #    print

    def test_drilldown_author(self):
        from django.test.client import Client
        from django.core.urlresolvers import reverse
        
        from softwarefabrica.django.drilldown.views import *

        c = Client()

        url = reverse('drilldown-generic-drilldown',
                      kwargs={'app_label' : 'tests',
                              'model_name': 'author',
                              'url'       : ''})
        response = c.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'drilldown/object_drilldown.html')
        #logging.debug(response)
        context = response.context[-1]
        #logging.debug(context)
        self.assertEqual(context['object_name'], 'author')
        self.assertTrue(isinstance(context['ddinfo'], DrillDownInfo))
        ddinfo = context['ddinfo']
        self.assertEqual(context['used_fields'], ddinfo.used_fields)
        self.assertEqual(len(ddinfo.used_fields), 0)
        self.assertEqual(context['remaining_fields'], ddinfo.remaining_fields)
        #self.assertEqual(len(ddinfo.remaining_fields), len(Author._meta.fields))
        self.assertEqual(len(ddinfo.remaining_fields), 0)
        self.assertEqual(ddinfo.pivot_field, None)
        self.assertEqual(len(ddinfo.pivot_field_values), 0)

        url = reverse('drilldown-generic-drilldown',
                      kwargs={'app_label' : 'tests',
                              'model_name': 'author',
                              'url'       : 'last_name/'})
        response = c.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'drilldown/object_drilldown.html')
        #logging.debug(response)
        context = response.context[-1]
        #logging.debug(context)
        self.assertEqual(context['object_name'], 'author')
        self.assertTrue(isinstance(context['ddinfo'], DrillDownInfo))
        ddinfo = context['ddinfo']
        self.assertEqual(context['used_fields'], ddinfo.used_fields)
        self.assertEqual(len(ddinfo.used_fields), 0)
        self.assertEqual(context['remaining_fields'], ddinfo.remaining_fields)
        #self.assertEqual(len(ddinfo.remaining_fields), len(Author._meta.fields))
        self.assertEqual(len(ddinfo.remaining_fields), 0)
        logging.debug(ddinfo.pivot_field)
        logging.debug(ddinfo.pivot_field_values)
        self.assertEqual(ddinfo.pivot_field.name, 'last_name')
        self.assertEqual(len(ddinfo.pivot_field_values), 1)

        url = reverse('drilldown-generic-drilldown',
                      kwargs={'app_label' : 'tests',
                              'model_name': 'author',
                              'url'       : 'last_name/Alighieri/'})
        response = c.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'drilldown/object_drilldown.html')
        #logging.debug(response)
        context = response.context[-1]
        #logging.debug(context)
        self.assertEqual(context['object_name'], 'author')
        self.assertTrue(isinstance(context['ddinfo'], DrillDownInfo))
        ddinfo = context['ddinfo']
        self.assertEqual(context['used_fields'], ddinfo.used_fields)
        self.assertEqual(len(ddinfo.used_fields), 1)
        self.assertEqual(ddinfo.used_fields[0].name, 'last_name')
        self.assertEqual(ddinfo.used_fields[0].value, 'Alighieri')
        self.assertEqual(context['remaining_fields'], ddinfo.remaining_fields)
        #self.assertEqual(len(ddinfo.remaining_fields), len(Author._meta.fields)-1)
        self.assertEqual(len(ddinfo.remaining_fields), 0)
        self.assertEqual(ddinfo.pivot_field, None)
        self.assertEqual(len(ddinfo.pivot_field_values), 0)
