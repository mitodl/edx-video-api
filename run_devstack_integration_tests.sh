#!/bin/bash
set -e

source /edx/app/edxapp/venvs/edxapp/bin/activate

cd /edx/app/edxapp/edx-platform
mkdir -p reports

pip install -r requirements/edx/testing.txt

cd /edx-video-api
pip install -e .

# output the packages which are installed for logging
pip freeze

cp /edx/app/edxapp/edx-platform/setup.cfg .
rm ./pytest.ini
mkdir test_root  # for edx

pytest --no-pylint ./tests/integration_tests.py
