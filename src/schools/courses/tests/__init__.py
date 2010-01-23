from decimal import Decimal
from django.test.testcases import TestCase
from schools.courses.models import Lesson, LessonAttendee, CourseMember
from django.core.urlresolvers import reverse


class LectorPriceTest(TestCase):
    fixtures = ['pricetest']
    
    def test_price_from_contract(self):
        lesson = Lesson.objects.get(pk=1)
        self.assertEquals(False, lesson.realized)
        
        lesson.fill_attendance().save()
        self.assertEquals(Decimal(5), lesson.real_lector_price)
        
    def test_price_from_hour_rate(self):
        lesson = Lesson.objects.get(pk=2)
        self.assertEquals(False, lesson.realized)
        
        lesson.fill_attendance().save()
        self.assertEquals(Decimal(1), lesson.real_lector_price)
        
class CourseMemberPriceTest(TestCase):
    fixtures = ['pricetest']
    
    def test_course_member_price(self):
        lesson = Lesson.objects.get(pk=1)
        self.assertEquals(False, lesson.realized)
        self.assertEquals(None, LessonAttendee.objects.get(pk=1).course_member_price)
        self.assertEquals(None, LessonAttendee.objects.get(pk=2).course_member_price)
        self.assertEquals(None, LessonAttendee.objects.get(pk=3).course_member_price)
        
        lesson.fill_attendance().save()
        self.assertEquals(Decimal(3), LessonAttendee.objects.get(pk=1).course_member_price)
        self.assertEquals(Decimal(1), LessonAttendee.objects.get(pk=2).course_member_price)
        self.assertEquals(Decimal(1), LessonAttendee.objects.get(pk=3).course_member_price)
        
class CourseMemberTest(TestCase):
    fixtures = ['pricetest']
    
    def test_coursemember_add(self):
        self.client.login(username='tomas', password='tomas')
        response = self.client.get(reverse('courses_coursemember_create', kwargs={'course_id':'1'}))
        self.assertEquals(200, response.status_code)
        course_members_count = CourseMember.objects.count()
        response = self.client.post(reverse('courses_coursemember_create', kwargs={'course_id':'1'}), 
                         {'student':'1','start':'01.01.2009', 'expense_group':'1', 'course':'1'})
        
        self.assertRedirects(response, reverse('courses_coursemember_update', kwargs={'course_id':'1', 'object_id':'4'}))
        self.assertEquals(course_members_count+1, CourseMember.objects.count())
        
class CourseTest(TestCase):
    fixtures = ['pricetest']
    
    def test_course_create(self):
        self.client.login(username='tomas', password='tomas')
        response = self.client.get(reverse('courses_course_create'))
        self.assertEquals(200, response.status_code)
        
        response = self.client.post(reverse('courses_course_create'), 
                                    {'responsible':'1', 'lector':'1', 'name':'xxx', 'language':'en'})
        self.assertRedirects(response, reverse('courses_course_update', kwargs={'object_id': '3'}))