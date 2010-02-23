from django.contrib.auth.models import User
from django.test.testcases import TestCase
from schools.students.models import Student
from django.core.urlresolvers import reverse

class StudentTest(TestCase):
    fixtures = ['students']
    
    def setUp(self):
        self.client.login(username='tomas', password='tomas')
        
    def test_create_student(self):
        before = User.objects.count()
        response = self.client.get(reverse('students_student_create'))
        self.assertEquals(200, response.status_code)
        
        response = self.client.post(reverse('students_student_create'), {'first_name':'first', 'last_name':'last', 'username':'username'})
        self.assertRedirects(response, reverse('students_student_update', kwargs={'object_id':'2'}))
        
        student = Student.objects.get(pk=2)
        self.assertTrue(student.user is not None)
        self.assertEquals(before + 1, User.objects.count())
        
    def test_update_student(self):
        response = self.client.post(reverse('students_student_update', kwargs={'object_id':'1'}), {'first_name':'first', 'last_name':'last', 'username':'username'})
        self.assertRedirects(response, reverse('students_student_update', kwargs={'object_id':'1'}))
        
        self.assertEquals('first', Student.objects.get(pk=1).user.first_name)
        self.assertEquals('last', Student.objects.get(pk=1).user.last_name)
        self.assertEquals('username', Student.objects.get(pk=1).user.username)