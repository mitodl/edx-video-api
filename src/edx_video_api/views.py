"""
edX video API views
"""
from functools import wraps
from uuid import uuid4
import m3u8

from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import permissions, status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from edxval.api import (
    create_video,
    get_videos_for_course,
    get_videos_for_ids,
)
from edxval.exceptions import ValCannotCreateError
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

OAuth2Authentication = import_string(settings.VIDEO_API["AUTHENTICATION_CLASS"])
ApiKeyHeaderPermission = import_string(settings.VIDEO_API["API_KEY_PERMISSION_CLASS"])
CourseOverview = import_string(settings.VIDEO_API["COURSE_OVERVIEW"])
ERROR_KEY = "error"


def dict_without_keys(d, *omitkeys):
    """
    Returns a copy of a dict without the specified keys
    Args:
        d (dict): A dict that to omit keys from
        *omitkeys: Variable length list of keys to omit
    Returns:
        dict: A dict with omitted keys
    """
    return {key: d[key] for key in d.keys() if key not in omitkeys}


def is_valid_hls_url(hls_url):
    """
    Checks if a given URL points to a valid HLS manifest
    """
    try:
        manifest = m3u8.load(hls_url)
        return bool(len(manifest.media) or len(manifest.playlists))
    except:  # pylint: disable=bare-except
        return False


def verify_course_exists(view_func):
    """
    A decorator to wrap a view function that takes a course id parameter

    Returns:
        An error response if the course id is invalid, or if no associated `CourseOverview` exists.
    """
    @wraps(view_func)
    def wrapped_function(self, request, **kwargs):
        """
        Wraps the given view function
        """
        course_id = kwargs.get("course_id")
        try:
            course_key = CourseKey.from_string(course_id)
            if CourseOverview.get_from_id_if_exists(course_key) is None:
                return Response(
                    {ERROR_KEY: u"Course with id '{}' not found".format(course_id)},
                    status=status.HTTP_404_NOT_FOUND
                )
        except InvalidKeyError:
            return Response(
                {ERROR_KEY: u"Invalid course key ('{}')".format(course_id)},
                status=status.HTTP_404_NOT_FOUND
            )
        return view_func(self, request, **kwargs)
    return wrapped_function


def json_serialize_video(serialized_video):
    """Returns a JSON-serializable version of an edxval-serialized video object"""
    return {
        "encoded_videos": [
            dict_without_keys(encoded_video, "created", "modified")
            for encoded_video in serialized_video["encoded_videos"]
        ],
        "url": serialized_video["url"],
        "edx_video_id": serialized_video["edx_video_id"],
        "client_video_id": serialized_video["client_video_id"],
        "duration": serialized_video["duration"],
        "status": serialized_video["status"]
    }


class CourseVideoListView(ListCreateAPIView):
    """Video API views"""
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (permissions.IsAdminUser, ApiKeyHeaderPermission)

    @verify_course_exists
    def list(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """Returns serialized videos for a course"""
        course_id = kwargs.get("course_id")
        return Response([
            json_serialize_video(serialized_video)
            for serialized_video in list(get_videos_for_course(course_id)[0])
        ])

    @verify_course_exists
    def create(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Creates an HLS video object for a course and returns a serialized version of the
        newly-created video object
        """
        course_id = kwargs.get("course_id")
        file_name = request.data.get("filename")
        hls_url = request.data.get("hls_url")
        error = None
        if not file_name:
            error = u"Request does not contain file name"
        if not hls_url:
            error = u"Request does not contain HLS URL"
        elif not is_valid_hls_url(hls_url):
            error = u"Request does not contain a valid HLS URL"
        if error:
            return Response(
                {ERROR_KEY: error},
                status=status.HTTP_400_BAD_REQUEST
            )

        edx_video_id = unicode(uuid4())
        try:
            video_id = create_video({
                "edx_video_id": edx_video_id,
                "status": "file_complete",
                "client_video_id": file_name,
                "duration": 0,
                "encoded_videos": [{"profile": "hls", "url": hls_url, "bitrate": 0, "file_size": 0}],
                "courses": [course_id]
            })
        except ValCannotCreateError as exc:
            return Response(
                {ERROR_KEY: u"Could not create video (exception: {})".format(str(exc))},
                status=status.HTTP_400_BAD_REQUEST
            )
        serialized_video = next(get_videos_for_ids([video_id]))
        return Response(json_serialize_video(serialized_video))
