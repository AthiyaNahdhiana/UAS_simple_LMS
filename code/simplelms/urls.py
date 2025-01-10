"""
URL configuration for simplelms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from lms_core.views import index, testing, addData, editData, deleteData
from lms_core.api import apiv1
from lms_core.views import (
    UserActivityDashboardView,
    CourseAnalyticsView,
    BatchEnrollView,
    ModerateCommentView,
    ViewContentComments,
    GenerateCertificateView,
)

urlpatterns = [
    path('api/v1/', apiv1.urls),
    path('admin/', admin.site.urls),
    path('testing/', testing),
    path('tambah/', addData),
    path('ubah/', editData),
    path('hapus/', deleteData),
    path('', index),
    path('user-activity/<int:user_id>/', UserActivityDashboardView.as_view(), name='user_activity_dashboard'),
    path('course-analytics/<int:course_id>/', CourseAnalyticsView.as_view(), name='course_analytics'),
    path('batch-enroll/<int:course_id>/', BatchEnrollView.as_view(), name='batch_enroll'),
    path('moderate-comment/<int:comment_id>/', ModerateCommentView.as_view(), name='moderate_comment'),
    path('view-content-comments/<int:course_id>/', ViewContentComments.as_view(), name='view_content_comments'),
    path('generate-certificate/<int:course_id>/', GenerateCertificateView.as_view(), name='generate_certificate'),
]
