from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

class ContractTest(TestCase):
    fixtures = ['test_lectors']
    def test_contract_add(self):
        self.client.login(username='tomas', password='tomas')
        response = self.client.get(reverse('lectors_contract_create', kwargs={'lector_id':'1'}))
        self.assertEquals(200, response.status_code)
        self.assertContains(response, '<input type="hidden" name="lector" value="1" id="id_lector" />')
        
        response = self.client.post(reverse('lectors_contract_create', kwargs={'lector_id':'1'}), 
                         {'lector':'1', 'contract_number':'2009/10', 'hour_rate':'5', 'start':'1.1.2009', 'end':'31.12.2009',
                          'hourrate_set-INITIAL_FORMS':'0', 'hourrate_set-TOTAL_FORMS':'3'})
        self.assertRedirects(response, reverse('lectors_contract_update', kwargs={'lector_id':'1', 'object_id':'2'}))