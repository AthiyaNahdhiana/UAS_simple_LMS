from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from lms_core.models import Course
from django.core import serializers
from django.contrib.auth.models import User
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from lms_core.models import Course, CourseMember, CourseContent, Comment, ContentCompletion, Certificate, Feedback
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
import json

def index(request):
    return HttpResponse("<h1>Hello World</h1>")
    
def testing(request):
    dataCourse = Course.objects.all()
    dataCourse = serializers.serialize("python", dataCourse)
    return JsonResponse(dataCourse, safe=False)

def addData(request): # jangan lupa menambahkan fungsi ini di urls.py
    course = Course(
        name = "Belajar Django",
        description = "Belajar Django dengan Mudah",
        price = 1000000,
        teacher = User.objects.get(username="admin")
    )
    course.save()
    return JsonResponse({"message": "Data berhasil ditambahkan"})

def editData(request):
    course = Course.objects.filter(name="Belajar Django").first()
    course.name = "Belajar Django Setelah update"
    course.save()
    return JsonResponse({"message": "Data berhasil diubah"})

def deleteData(request):
    course = Course.objects.filter(name__icontains="Belajar Django").first()
    course.delete()
    return JsonResponse({"message": "Data berhasil dihapus"})

# Utility to handle JSON parsing errors
def parse_json_body(request):
    try:
        return json.loads(request.body), None
    except json.JSONDecodeError:
        return None, JsonResponse({'error': 'Invalid JSON format'}, status=400)
    
class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')  # Redirect to login page after registration

class UserActivityDashboardView(View):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            courses_as_student = CourseMember.objects.filter(user_id=user, roles='std').count()
            courses_created = Course.objects.filter(teacher=user).count()
            comments_written = Comment.objects.filter(member_id__user_id=user).count()
            contents_completed = ContentCompletion.objects.filter(user_id=user).count()

            data = {
                'username': user.username,
                'courses_as_student': courses_as_student,
                'courses_created': courses_created,
                'comments_written': comments_written,
                'contents_completed': contents_completed,
            }
            return JsonResponse(data)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

class CourseAnalyticsView(View):
    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            members_count = CourseMember.objects.filter(course_id=course).count()
            contents_count = CourseContent.objects.filter(course_id=course).count()
            comments_count = Comment.objects.filter(content_id__course_id=course).count()
            feedback_count = Feedback.objects.filter(course_id=course).count()

            data = {
                'course_name': course.name,
                'members_count': members_count,
                'contents_count': contents_count,
                'comments_count': comments_count,
                'feedback_count': feedback_count,
            }
            return JsonResponse(data)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class BatchEnrollView(View):
    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            if request.user != course.teacher:
                return JsonResponse({'error': 'Only the course teacher can enroll students'}, status=403)

            body, error = parse_json_body(request)
            if error:
                return error

            student_ids = body.get('student_ids', [])
            if not isinstance(student_ids, list):
                return JsonResponse({'error': 'Invalid data format'}, status=400)

            for student_id in student_ids:
                student = User.objects.get(id=student_id)
                CourseMember.objects.get_or_create(course_id=course, user_id=student, roles='std')

            return JsonResponse({'message': f'{len(student_ids)} students enrolled successfully.'})
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'error': 'One or more users not found'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class ModerateCommentView(View):
    def post(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
            if request.user != comment.content_id.course_id.teacher:
                return JsonResponse({'error': 'Only the course teacher can moderate comments'}, status=403)

            body, error = parse_json_body(request)
            if error:
                return error

            is_moderated = body.get('is_moderated')
            if is_moderated is None:
                return JsonResponse({'error': 'Invalid data format'}, status=400)

            comment.is_moderated = is_moderated
            comment.save()

            return JsonResponse({'message': 'Comment moderation updated successfully.'})
        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Comment not found'}, status=404)

class ViewContentComments(View):
    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            comments = Comment.objects.filter(content_id__course_id=course, is_moderated=True).values(
                'member_id__user_id__username', 'comment', 'id'
            )
            return JsonResponse({'comments': list(comments)})
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)

class GenerateCertificateView(View):
    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            user = request.user

            total_contents = CourseContent.objects.filter(course_id=course).count()
            completed_contents = ContentCompletion.objects.filter(user_id=user, course_id=course).count()

            if total_contents == 0 or completed_contents < total_contents:
                return JsonResponse({'error': 'Course not yet completed'}, status=403)

            certificate, _ = Certificate.objects.get_or_create(user_id=user, course_id=course)

            certificate_html = render_to_string('certificate.html', { # type: ignore
                'user': user,
                'course': course,
                'issued_at': certificate.issued_at,
            })

            return JsonResponse({'certificate': certificate_html})
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)
