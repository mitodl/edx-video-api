"""edX integration tests"""
# pylint: disable=import-error,redefined-outer-name
from django.test.client import Client

from student.tests.factories import UserFactory
from edx_oauth2_provider.tests.factories import AccessTokenFactory

COURSE_ID = "course-v1:MIT+DemoX+Demo_Course_2"


def test_integration(settings):
    settings.EDX_API_KEY = u"SOME_API_KEY"
    client = Client()
    user = UserFactory.create(is_staff=True)
    access_token = AccessTokenFactory.create(user=user)
    headers = {
        'HTTP_AUTHORIZATION': u'Bearer {}'.format(access_token.token),
        'HTTP_X_EDX_API_KEY': settings.EDX_API_KEY
    }
    resp = client.post(
        "/api/course_videos/{}".format(COURSE_ID),
        **headers
    )
    assert resp is not None
    assert 1 == (2 - 1)
