import pytest
from django.test import TestCase

from oauth2_provider_jwt.utils import validate_uuid


class ValidateUUIDTests(TestCase):
    def test_invalid_uuid(self):
        result = validate_uuid("invalid_uuid")
        self.assertFalse(result)

    def test_valid_uuid(self):
        result = validate_uuid("e28163ce-b86d-4145-8df3-c8dad2e0b601")
        self.assertTrue(result)
