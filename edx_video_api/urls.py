"""Project URL Configuration"""

from django.conf.urls import url

from edx_video_api.views import CourseVideoListView


urlpatterns = [
    url(r"^(?P<course_id>[^/]*)/$", CourseVideoListView.as_view(), name="course-videos"),
]
