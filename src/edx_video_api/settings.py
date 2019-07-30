"""Settings to provide to edX"""


def plugin_settings(settings):
    """Populate settings"""
    settings.VIDEO_API = dict(
        AUTHENTICATION_CLASS="openedx.core.lib.api.authentication.OAuth2AuthenticationAllowInactiveUser",
        API_KEY_PERMISSION_CLASS="openedx.core.lib.api.permissions.ApiKeyHeaderPermission",
        COURSE_OVERVIEW="openedx.core.djangoapps.content.course_overviews.models.CourseOverview"
    )
