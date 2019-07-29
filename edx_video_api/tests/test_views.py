"""Tests for video API views"""
# pylint: disable=redefined-outer-name
import json
from collections import namedtuple

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from edxval.exceptions import ValCannotCreateError
from opaque_keys import InvalidKeyError
from edx_video_api.views import (
    CourseVideoListView,
    json_serialize_video,
)

from .utils import generate_video_api_result, now_in_utc, is_subdict

COURSE_ID = "course-v1:MIT+DemoX+Demo_Course_2"
FILENAME = "My Video"
HLS_URL = "http://example.com/video.m3u8"


@pytest.fixture()
def view():
    """Fixture for an instance of the video API view"""
    return CourseVideoListView.as_view()


@pytest.fixture(autouse=True)
def edxval_api(mocker):
    """Fixture for mocked API functions from edxval"""
    EdxvalApi = namedtuple(
        "EdxvalApi",
        "get_videos_for_course,get_videos_for_ids,create_video"
    )
    mock_video_result = generate_video_api_result(COURSE_ID)
    patched_get_videos = mocker.patch(
        "edx_video_api.views.get_videos_for_course",
        return_value=(iter([mock_video_result]), mocker.Mock())
    )
    patched_get_videos_for_ids = mocker.patch(
        "edx_video_api.views.get_videos_for_ids",
        return_value=iter([mock_video_result])
    )
    patched_create_video = mocker.patch(
        "edx_video_api.views.create_video",
        return_value=123
    )
    return EdxvalApi(
        get_videos_for_course=patched_get_videos,
        get_videos_for_ids=patched_get_videos_for_ids,
        create_video=patched_create_video,
    )


@pytest.fixture()
def patched_valid_hls(mocker):
    """Fixture that patches is_valid_hls_url"""
    return mocker.patch(
        "edx_video_api.views.is_valid_hls_url",
        return_value=True
    )


@pytest.fixture()
def get_request():
    """Fixture for a GET request to the video API view"""
    factory = APIRequestFactory()
    return factory.get("/{}/".format(COURSE_ID))


@pytest.fixture()
def post_request():
    """Fixture for a POST request to the video API view"""
    factory = APIRequestFactory()
    return factory.post(
        "/{}/".format(COURSE_ID),
        {
            "filename": FILENAME,
            "hls_url": HLS_URL
        }
    )


def test_json_serialize_video():
    """
    json_serialize_video should take a video serialized by the edxval API and further serialize it to be JSON-safe
    """
    now = now_in_utc()
    video_api_result = {
        "encoded_videos": [
            {
                "url": "/some/video/url/",
                "file_size": 0,
                "bitrate": 0,
                "profile": u"hls",
                "created": now,
                "modified": now,
            }
        ],
        "url": "/some/url/",
        "edx_video_id": "some-uuid",
        "client_video_id": "filename",
        "duration": 0.0,
        "status": "file_complete",
        "created": now,
        "courses": [
            {"some-course-id": None}
        ],
    }
    assert json_serialize_video(video_api_result) == {
        "encoded_videos": [
            {
                "url": "/some/video/url/",
                "file_size": 0,
                "bitrate": 0,
                "profile": u"hls"
            }
        ],
        "url": video_api_result["url"],
        "edx_video_id": video_api_result["edx_video_id"],
        "client_video_id": video_api_result["client_video_id"],
        "duration": video_api_result["duration"],
        "status": video_api_result["status"]
    }


@pytest.mark.parametrize('mock_request', [
    pytest.lazy_fixture('get_request'),
    pytest.lazy_fixture('post_request'),
])
def test_view_bad_course_key_fail(mocker, view, mock_request):
    """A request to the video API with an invalid course id/key should fail"""
    patched_course_key_parser = mocker.patch(
        "edx_video_api.views.CourseKey.from_string",
        side_effect=InvalidKeyError(mocker.Mock(), {})
    )
    response = view(mock_request, course_id=COURSE_ID).render()
    patched_course_key_parser.assert_called_once_with(COURSE_ID)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Invalid course key" in json.loads(response.content)["error"]


@pytest.mark.parametrize('mock_request', [
    pytest.lazy_fixture('get_request'),
    pytest.lazy_fixture('post_request'),
])
def test_view_nonexistent_course_fail(mocker, view, mock_request):
    """A request to the video API with a course key that does not have a matching course should fail"""
    patched_course_key_parser = mocker.patch(
        "edx_video_api.views.CourseOverview.get_from_id_if_exists",
        return_value=None
    )
    response = view(mock_request, course_id=COURSE_ID).render()
    patched_course_key_parser.assert_called_once()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in json.loads(response.content)["error"]


def test_view_get_success(mocker, view, get_request, edxval_api):
    """A successful GET request to the video API should return JSON-serialized videos"""
    mock_serialized_video = {"serialized": "video"}
    patched_serializer = mocker.patch(
        "edx_video_api.views.json_serialize_video",
        return_value=mock_serialized_video
    )
    response = view(get_request, course_id=COURSE_ID).render()
    edxval_api.get_videos_for_course.assert_called_once()
    patched_serializer.assert_called_once()
    assert json.loads(response.content) == [mock_serialized_video]


@pytest.mark.parametrize('filename,hls_url', [
    (None, HLS_URL),
    (FILENAME, None)
])
def test_create_missing_data_fail(view, filename, hls_url):
    """A POST request to the video API without required values in the body should fail"""
    factory = APIRequestFactory()
    request = factory.post(
        "/{}/".format(COURSE_ID),
        {
            "filename": filename,
            "hls_url": hls_url
        }
    )
    response = view(request, course_id=COURSE_ID).render()
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_video_fail(view, post_request, patched_valid_hls, edxval_api):  # pylint: disable=unused-argument
    """A POST request to the video API that causes an edxval API failure should return a meaningful response"""
    edxval_api.create_video.side_effect = ValCannotCreateError
    response = view(post_request, course_id=COURSE_ID).render()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Could not create video" in json.loads(response.content)["error"]


def test_create_video_success(view, post_request, patched_valid_hls, edxval_api):
    """A successful POST request to the video API should create a video object and return the serialized version"""
    response = view(post_request, course_id=COURSE_ID).render()
    assert response.status_code == status.HTTP_200_OK
    patched_valid_hls.assert_called_once()
    edxval_api.create_video.assert_called_once()
    create_video_call_arg = edxval_api.create_video.call_args[0][0]
    assert is_subdict({
        "status": "file_complete",
        "client_video_id": FILENAME,
        "duration": 0,
        "encoded_videos": [{
            "profile": "hls",
            "url": HLS_URL,
            "bitrate": 0,
            "file_size": 0
        }],
        "courses": [COURSE_ID]
    }, create_video_call_arg)
    new_video_id = edxval_api.create_video.return_value
    edxval_api.get_videos_for_ids.assert_called_once_with([new_video_id])
