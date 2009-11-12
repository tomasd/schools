from decimal import Decimal
from django.test.testcases import TestCase
from schools.courses.models import Lesson, LessonAttendee


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