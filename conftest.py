import secrets
from os import environ as env

import pytest

from authprofiles import models as auth_profile_models


@pytest.mark.django_db
@pytest.fixture(scope="function")
def create_new_passport_application(db):
    scope_1 = auth_profile_models.PassportScope.objects.create(name="blender.read", description="blender read")
    scope_2 = auth_profile_models.PassportScope.objects.create(name="blender.write", description="blender write")

    api = auth_profile_models.PassportAPI.objects.create(identifier="blender.utm.dev.airoplatform.com", name="Blender API")
    api.scopes.add(scope_1, scope_2)
    # Generate a new client_id and client_secret
    # WARNING: This is not a secure way to generate client_id and client_secret
    # This is only for testing purposes. This should not happen in production.
    client_id = secrets.token_urlsafe(32)
    client_secret = secrets.token_urlsafe(64)

    app = auth_profile_models.PassportApplication.objects.create(
        name="Blender client",
        client_type=auth_profile_models.PassportApplication.CLIENT_PUBLIC,
        authorization_grant_type=auth_profile_models.PassportApplication.GRANT_CLIENT_CREDENTIALS,
        client_class=0,
        client_id=client_id,
        client_secret=client_secret,
    )
    app.audience.add(api)
    env.setdefault("UNIT_TEST_CLIENT_ID", client_id)
    env.setdefault("UNIT_TEST_CLIENT_SECRET", client_secret)

    yield
    auth_profile_models.PassportScope.objects.all().delete()
    auth_profile_models.PassportAPI.objects.all().delete()
    auth_profile_models.PassportApplication.objects.all().delete()
