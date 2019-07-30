"""AppConfig for edX Video API"""
from django.apps import AppConfig

from openedx.core.djangoapps.plugins.constants import (  # pylint: disable=import-error
    ProjectType,
    SettingsType,
    PluginURLs,
    PluginSettings,
)


class EdxVideoApiAppConfig(AppConfig):
    """
    AppConfig for edX Video API
    """
    name = "edx_video_api"

    # NOTE: Studio is where users can upload videos via UI when edxval is installed, but these new endpoints are
    # being added to LMS. This is because LMS is configured to accept an API key ("EDX_API_KEY" in LMS settings) and
    # Studio is not.
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: u'',
                PluginURLs.REGEX: r'^api/course_videos/',
                PluginURLs.RELATIVE_PATH: u'urls',
            }
        },
        PluginSettings.CONFIG: {
            ProjectType.LMS: {
                SettingsType.COMMON: {
                    PluginSettings.RELATIVE_PATH: u'settings'
                },
            }
        }
    }
