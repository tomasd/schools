from decimal import Decimal #@UnresolvedImport
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory
from django.test.testcases import TestCase
from schools.buildings.models import Classroom
from schools.courses.forms import LessonRealizedForm1, LessonPlanForm
from schools.courses.models import Lesson, LessonAttendee, CourseMember, Course
from schools.lectors.models import Lector


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
                         {'student':'1', 'start':'01.01.2009', 'expense_group':'1', 'course':'1'})
        
        self.assertRedirects(response, reverse('courses_coursemember_update', kwargs={'course_id':'1', 'object_id':'4'}))
        self.assertEquals(course_members_count + 1, CourseMember.objects.count())
        
class CourseTest(TestCase):
    fixtures = ['pricetest']
    
    def test_course_create(self):
        self.client.login(username='tomas', password='tomas')
        response = self.client.get(reverse('courses_course_create'))
        self.assertEquals(200, response.status_code)
        
        response = self.client.post(reverse('courses_course_create'),
                                    {'responsible':'1', 'lector':'1', 'name':'xxx', 'language':'en'})
        self.assertRedirects(response, reverse('courses_course_update', kwargs={'object_id': '3'}))
        
class LessonRealizedForm1Test(TestCase):
    fixtures = ['pricetest']
    
    def test_display(self):
        form = LessonRealizedForm1(instance=Lesson.objects.get(pk=1))
        self.assertEquals(3, len(form.fields['lesson_attendees'].queryset))
        unicode(form)
        
    def test_save(self):
        data = {
                'lesson':1,
                'real_classroom': Classroom.objects.get(pk=1).pk,
                'real_lector':Lector.objects.get(pk=1).pk,
                'real_start_0':'1.12.2009', 'real_start_1':'10:30',
                'real_end_0':'1.12.2009', 'real_end_1':'12:00',
                'real_content':'xxx',
                'lesson_attendees':['1', '2']}
        form = LessonRealizedForm1(instance=Lesson.objects.get(pk=1), data=data)
        self.assertTrue(form.is_valid(), form.errors.items())
        self.assertEquals(2, len(form.cleaned_data['lesson_attendees']))
        lesson = form.save()
        self.assertTrue(lesson.realized)
        self.assertEquals(2, lesson.lessonattendee_set.filter(present=True).count())
        
    def test_formset(self):
        LessonFormSet = formset_factory(LessonRealizedForm1, extra=0, can_delete=False)
        form = LessonFormSet(initial=[{'lesson':1}])
        unicode(form)
        
class LessonPlanFormTest(TestCase):
    fixtures = ['pricetest']
    
    def testValidationInvalid(self):
        data = {
                'course':'1',
                'classroom':'1',
                'start_0':'1.1.2009', 'start_1':' 10:30',
                'end_0':'1.1.2009', 'end_1':' 11:30',
        }
        form = LessonPlanForm(data)
        self.assertFalse(form.is_valid())
        
    def testValidationValid(self):
        data = {
                'course':'1',
                'classroom':'1',
                'start_0':'1.1.2009', 'start_1':'9:30',
                'end_0':'1.1.2009', 'end_1':'9:59',
        }
        form = LessonPlanForm(data)
        self.assertTrue(form.is_valid(), form.errors)
