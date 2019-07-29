"""Test suite utility functions/classes"""
import datetime
from uuid import uuid4
import pytz
from mock import Mock
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission


class DummyOAuth2Authentication(BaseAuthentication):
    """View authentication class for use in the test suite"""
    def authenticate(self, request):
        return Mock(), Mock()


class DummyApiKeyHeaderPermission(BasePermission):
    """View permission class for use in the test suite"""
    def has_permission(self, request, view):
        return True


class DummyCourseOverview(object):
    """CourseOverview class for use in the test suite"""
    @staticmethod
    def get_from_id_if_exists(course_key):  # pylint: disable=unused-argument
        return True


def now_in_utc():
    """Returns the current datetime in UTC"""
    return datetime.datetime.now(tz=pytz.UTC)


def is_subdict(dict_to_test, master_dict):
    """Returns True if the first dict is a subset of the second dict"""
    result = False
    try:
        for pkey, pvalue in dict_to_test.items():
            if isinstance(pvalue, dict):
                result = is_subdict(pvalue, master_dict[pkey])
                if not result:
                    break
            else:
                assert master_dict[pkey] == pvalue
                result = True
    except (AssertionError, KeyError):
        result = False
    return result


def generate_video_api_result(course_id):
    """Generates a mock single API result in the same from that edxval returns"""
    now = now_in_utc()
    uuid = unicode(uuid4())
    filename = u"My File"
    url = u"https://example.com/{}.m3u8".format(uuid)
    return {
        "status": u"file_complete",
        "created": now,
        "url": u"/api/val/v0/videos/{}".format(uuid),
        "client_video_id": filename,
        "encoded_videos": [
            {
                "created": now,
                "modified": now,
                "url": url,
                "file_size": 0,
                "bitrate": 0,
                "profile": u"hls"
            }
        ],
        "courses": [
            {course_id: None}
        ],
        "duration": 0.0,
        "edx_video_id": uuid
    }
