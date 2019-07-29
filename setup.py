"""Setup for edX Video API"""
import os
from setuptools import setup, find_packages

VERSION = "0.0.1"


def package_data(pkg, root_list):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for root in root_list:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement;
    that is, it is not blank, a comment, or editable.
    """
    # Remove whitespace at the start/end of the line
    line = line.strip()

    # Skip blank lines, comments, and editable installs
    return not (
        line == '' or
        line.startswith('-r') or
        line.startswith('#') or
        line.startswith('-e') or
        line.startswith('git+')
    )


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.
    Returns a list of requirement strings.
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.strip() for line in open(path).readlines()
            if is_requirement(line)
        )
    return list(requirements)


setup(
    name="edx_video_api",
    version=VERSION,
    description="EdX Video API",
    license="BSD",
    url="https://github.com/mitodl/edx-video-api",
    author="MITx",
    zip_safe=False,
    include_package_data=True,
    install_requires=load_requirements("requirements/base.txt", "requirements/django.txt"),
    tests_require=load_requirements("requirements/test.txt"),
    packages=find_packages(),
    package_data=package_data("src/edx_video_api", []),
    entry_points={
        "lms.djangoapp": [
            "edx_video_api = edx_video_api.apps:EdxVideoApiAppConfig"
        ],
    }
)
