from django.conf import settings
from django.test.simple import run_tests as django_test_runner
from django.test.simple import run_tests

from django.db.models.loading import get_app, get_apps

def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=None,
              **kwargs):
    """
    Test runner that only runs tests for the apps listed
    in ``settings.TEST_APPS``.
    ``settings.TEST_APPS`` must be a list of app labels, as defined in
    http://docs.djangoproject.com/en/dev/topics/testing/#defining-a-test-runner
    """
    # from http://ericholscher.com/blog/2009/jun/29/enable-setuppy-test-your-django-apps/
    # avoids testing the entire Django framework
    extra_tests = extra_tests or []
    app_labels = getattr(settings, "TEST_APPS", test_labels)
    return django_test_runner(app_labels,
                              verbosity=verbosity, interactive=interactive,
                              extra_tests=extra_tests, **kwargs)

def profile_tests(*args, **kwargs):
    """Test runner to perform profiling."""
    # based on:
    #   http://opensource.washingtontimes.com/blog/post/jquick/2009/02/making-django-unit-tests-work-you/
    try:
        import cProfile as profile
    except ImportError:
        import profile
    prof_file = getattr(settings,'TEST_PROFILE',None)
    profile.runctx('run_tests(*args, **kwargs)',
                   {'run_tests':run_tests,'args':args,'kwargs':kwargs},
                   {},
                   prof_file)

def hotshot_profile_tests(*args, **kwargs):
    """
    Test runner to perform profiling with the hotshot profiler.

    To view profiling results with KCacheGrind, run:

    hotshot2calltree hotshot_tests.prof > cachegrind.out.01
    """
    import hotshot
    # based on:
    #   http://opensource.washingtontimes.com/blog/post/jquick/2009/02/making-django-unit-tests-work-you/
    prof_file = getattr(settings,'TEST_PROFILE',None)
    prof = hotshot.Profile(prof_file)
    prof.runctx('run_tests(*args, **kwargs)',
                {'run_tests':run_tests,'args':args,'kwargs':kwargs},
                {})

