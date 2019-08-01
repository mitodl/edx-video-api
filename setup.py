"""Setup for edX Video API"""
import os
import re
import sys
from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)
abs_base_dir = os.path.abspath(base_dir)
src_dir = os.path.join(base_dir, "src")
# When executing the setup.py, we need to be able to import ourselves, this
# means that we need to add the src/ directory to the sys.path.
sys.path.insert(0, src_dir)


def find_version(*file_paths):
    """Returns the version number as defined in a python file located at the given file path"""
    with open(os.path.join(abs_base_dir, *file_paths), 'r') as fp:
        version_file = fp.read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


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
    version=find_version("src/edx_video_api", "__init__.py"),
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    python_requires='>=2.7,<3.0',
    install_requires=load_requirements("requirements/base.txt", "requirements/django.txt"),
    tests_require=load_requirements("requirements/test.txt"),
    entry_points={
        "lms.djangoapp": [
            "edx_video_api = edx_video_api.apps:EdxVideoApiAppConfig"
        ],
    }
)
