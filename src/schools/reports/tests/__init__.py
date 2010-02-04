from decimal import Decimal
from django.test.testcases import TestCase
from django.core.urlresolvers import reverse


class AnalyzaLekciohodinTest(TestCase):
    fixtures = ['reporttest']
    def test_x(self):
        response = self.client.get(reverse('lesson-analysis'))
        self.assertEquals(200, response.status_code)
        
        response = self.client.get(reverse('lesson-analysis'), {'start':'01.02.2010', 'end':'01.02.2010', 'show_courses':'on'})
        self.assertEquals(200, response.status_code)
        
        