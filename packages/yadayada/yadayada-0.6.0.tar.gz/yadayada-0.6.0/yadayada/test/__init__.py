from django.conf import settings
from django.test.simple import run_tests as orig_run_tests

def run_tests(*args, **kwargs):
    """ Test runner that only run tests for the apps
    listed in :setting:TEST_APPS
    """
    app_labels = settings.TEST_APPS
    return orig_run_tests(app_labels, **kwargs)
