"""Utilities for test modules"""
import os, unittest, doctest
from sets import Set

from django.core.serializers import deserialize
from django.db.models import get_apps
from django.test.simple import get_tests, run_tests as old_run_tests

def load_fixture(path, file_type='json'):
    """Load a fixture file"""
    fp = file(path)
    cont = fp.read()
    fp.close()

    for obj in deserialize(file_type, cont):
        obj.save()

def model_has_fields(model_class, fields):
    """Checks if a model class has all fields in fields list"""
    fields = Set(fields + ['id'])
    model_fields = Set([f.name for f in model_class._meta.fields])
    return fields == model_fields

def is_model_class_fk(model_class_from, field, model_class_to):
    """Returns True if field is ForeignKey to model class informed"""
    return issubclass(
            model_class_from._meta.get_field_by_name(field)[0].rel.to,
            model_class_to,
            )

def is_field_type(model_class_from, field, field_type):
    """Checks if a field of a model class if of the type informed.
    If field_type value is a class, it compares just the class of field,
    if field_type is an instance of a field type class, it compares the
    max_length, max_digits and decimal_places, blank and null"""
    field = model_class_from._meta.get_field_by_name(field)[0]

    return field.__class__ == field_type or\
           (field.__class__ == field_type.__class__ and\
            getattr(field, 'max_length', None) == getattr(field_type, 'max_length', None) and\
            getattr(field, 'null', None) == getattr(field_type, 'null', None) and\
            getattr(field, 'blank', None) == getattr(field_type, 'blank', None) and\
            getattr(field, 'editable', None) == getattr(field_type, 'editable', None) and\
            getattr(field, 'max_digits', None) == getattr(field_type, 'max_digits', None) and\
            getattr(field, 'decimal_places', None) == getattr(field_type, 'decimal_places', None) and\
            getattr(field, 'unique', None) == getattr(field_type, 'unique', None) and\
            getattr(field, 'primary_key', None) == getattr(field_type, 'primary_key', None) and\
            getattr(field, 'db_column', None) == getattr(field_type, 'db_column', None) and\
            getattr(field, 'db_index', None) == getattr(field_type, 'db_index', None)
            )

def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    """Test runner to support many DocTests *.txt files and TestUnits *.py
    using a setting TEST_FILES in app.tests module"""
    for app in get_apps():
        test_mod = get_tests(app)

        if not test_mod or hasattr(test_mod, 'suite'):
            continue

        suites = []

        # DocTest files
        for filename in getattr(test_mod, 'DOCTEST_FILES', []):
            try:
                suites.append(doctest.DocFileSuite(
                    filename,
                    package=test_mod,
                    encoding='utf-8',
                    ))
            except TypeError:
                suites.append(doctest.DocFileSuite(
                    filename,
                    package=test_mod,
                    ))

        # Unit Tests modules
        for module in getattr(test_mod, 'UNITTEST_MODULES', []):
            suites.append(unittest.TestLoader().loadTestsFromModule(module))

        # Sets the 'suites' attribute to test module
        if suites:
            print suites
            test_mod.suite = lambda: unittest.TestSuite(suites)

    return old_run_tests(test_labels, verbosity, interactive, extra_tests)

