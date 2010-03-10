from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
class StudentLectorTest(TestCase):
    fixtures = ['test_studentbook']
    
    def test_display(self):
        self.client.login(username='tomas', password='tomas')
        response = self.client.get(reverse('studentbook_lector', kwargs={'object_id':'1'}))
        self.assertEquals(200, response.status_code)