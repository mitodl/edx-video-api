"""Test suite settings"""
import django

VIDEO_API = dict(
    AUTHENTICATION_CLASS="edx_video_api.utils.DummyOAuth2Authentication",
    API_KEY_PERMISSION_CLASS="edx_video_api.utils.DummyApiKeyHeaderPermission",
    COURSE_OVERVIEW="edx_video_api.utils.DummyCourseOverview"
)

SECRET_KEY = "edx_video_api"
INSTALLED_APPS = [
    "edxval"
]

django.setup()
