from django.test import TestCase

def assert_raise_error(expected_error: Exception):
    def wrapper(func):
        def inner(cls: TestCase, *args, **kwargs):
            try:
                func(cls, *args, **kwargs)
                cls.assertTrue(False)
            
            except Exception as error:
                cls.assertEqual(error.__class__, expected_error.__class__)
                cls.assertEqual(str(error), str(expected_error))
        return inner
    return wrapper
