# edx-video-api
A django app plugin for edx-platform that adds HTTP API endpoints for interacting with video objects. The video
models/APIs themselves are provided by the [edx-val](https://github.com/edx/edx-val/) library.

## Setup

##### 1) Make sure `edxval` is listed as a dependency for your Open edX instance.

##### 2) Run `edx-platform` with this package installed.
Some options for doing this: 

- Publish this package to PyPI, add it as a requirement to `/requirements/base.in`, and run `make upgrade`
  in the `devstack` directory.
- Mount this repo directory to devstack, then add that path in `/requirements/private.txt`:
    ``` 
    -e /path/to/edx-video-api
    ```
- Use [odl_devstack_tools](https://github.com/mitodl/odl_devstack_tools) to mount and install this local package
  with an extra docker-compose file.

## Usage

In order to make a request to the HTTP API endpoints that this plugin adds to LMS, you'll need:

- The edx API key value for your Open edX instance (the default value for LMS is `PUT_YOUR_API_KEY_HERE`)
- An unexpired access token value for an edX admin user (these can be viewed/added in Django admin: 
  `<LMS_URL>/admin/oauth2_provider/accesstoken/`)
- A valid course id, e.g.: `course-v1:edX+DemoX+Demo_Course`

Here are a couple request examples using cURL: 

```bash
COURSE_ID="course-v1:My+Course+ID"
LMS_URL="edx.odl.local:18000"
ACCESS_TOKEN="myaccesstokenvalue"
API_KEY=PUT_YOUR_API_KEY_HERE

# Create an HLS video object for the given course
HLS_URL="https://video.example.com/video.m3u8"
FILENAME="Video added via cURL"
curl -X POST "http://$LMS_URL/api/course_videos/$COURSE_ID/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "X-EdX-Api-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filename": "'$FILENAME'", "hls_url": "'$HLS_URL'"}'

# Fetch all HLS video objects for 
curl -X GET "http://$LMS_URL/api/course_videos/$COURSE_ID/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "X-EdX-Api-Key: $API_KEY"
```

## Testing

#### Setup

Ideally in a virtual environment with Python 2.7 installed, install tox:

`pip install tox`

Tox manages the virtual environment for running our tests.

#### Running Tests

```bash
# Run all tests with linting
tox
# Run all tests without linting
tox -- --no-pylint
# Run specific test file
tox -- edx_video_api/tests/test_views.py
```
