import base64
import json
from os import environ as env

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


@pytest.fixture
def api_client():
    return APIClient()


class Oauth2ProvideJWTTokenPOSTTests(APITestCase):
    def setUp(self):
        self.api_url = reverse("oauth2_provider_jwt:token")

    def test_post_invalid_grant_type(self):
        data = {
            "grant_type": "invalid_grant_type",
        }
        headers = {
            "HTTP_Content-Type": "application/x-www-form-urlencoded",
        }
        response = self.client.post(self.api_url, data=data, follow=False, secure=False, **headers)

        self.assertEqual(response.json(), {"error": "unsupported_grant_type"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_invalid_client(self):
        client_id = "invalid_client_id"
        client_secret = "invalid_client_secret"

        auth_value = f"{client_id}:{client_secret}"
        auth_value_bytes = auth_value.encode("ascii")
        auth_value_b64 = base64.b64encode(auth_value_bytes).decode("ascii")

        headers = {
            "HTTP_Authorization": f"Basic {auth_value_b64}",
            "HTTP_Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "blender.read blender.write",
            "audience": "blender.utm.dev.airoplatform.com",
            "client_uuid": "e28163ce-b86d-4145-8df3-c8dad2e0b601",
        }
        response = self.client.post(self.api_url, content_type="", data=data, follow=False, secure=False, **headers)

        self.assertEqual(response.json(), {"error": "invalid_client"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @pytest.mark.usefixtures("create_new_passport_application")
    def test_post_valid_client_without_uuid(self):
        client_id = env.get("UNIT_TEST_CLIENT_ID", "")
        client_secret = env.get("UNIT_TEST_CLIENT_SECRET", "")

        auth_value = f"{client_id}:{client_secret}"
        auth_value_bytes = auth_value.encode("ascii")
        auth_value_b64 = base64.b64encode(auth_value_bytes).decode("ascii")

        headers = {
            "HTTP_Authorization": f"Basic {auth_value_b64}",
            "HTTP_Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "blender.read blender.write",
            "audience": "blender.utm.dev.airoplatform.com",
        }
        response = self.client.post(self.api_url, content_type="", data=data, follow=False, secure=False, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access_token", response.json())
        self.assertEqual(response.json()["expires_in"], 3600)
        self.assertEqual(response.json()["token_type"], "Bearer")
        self.assertEqual(response.json()["scope"], "blender.read blender.write")

    @pytest.mark.usefixtures("create_new_passport_application")
    def test_post_valid_client_with_invalid_uuid(self):
        client_id = env.get("UNIT_TEST_CLIENT_ID", "")
        client_secret = env.get("UNIT_TEST_CLIENT_SECRET", "")

        auth_value = f"{client_id}:{client_secret}"
        auth_value_bytes = auth_value.encode("ascii")
        auth_value_b64 = base64.b64encode(auth_value_bytes).decode("ascii")

        headers = {
            "HTTP_Authorization": f"Basic {auth_value_b64}",
            "HTTP_Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "blender.read blender.write",
            "audience": "blender.utm.dev.airoplatform.com",
            "client_uuid": "invalid_uuid",
        }
        response = self.client.post(self.api_url, content_type="", data=data, follow=False, secure=False, **headers)

        expected_response = {"error": "invalid_request", "error_description": "Invalid UUID. Please set the appropriate UUID in the request."}
        response_data = json.loads(response.json())
        self.assertEqual(response_data, expected_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.usefixtures("create_new_passport_application")
    def test_post_valid_client_with_uuid(self):
        client_id = env.get("UNIT_TEST_CLIENT_ID", "")
        client_secret = env.get("UNIT_TEST_CLIENT_SECRET", "")

        auth_value = f"{client_id}:{client_secret}"
        auth_value_bytes = auth_value.encode("ascii")
        auth_value_b64 = base64.b64encode(auth_value_bytes).decode("ascii")

        headers = {
            "HTTP_Authorization": f"Basic {auth_value_b64}",
            "HTTP_Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "blender.read blender.write",
            "audience": "blender.utm.dev.airoplatform.com",
            "client_uuid": "e28163ce-b86d-4145-8df3-c8dad2e0b601",
        }
        response = self.client.post(self.api_url, content_type="", data=data, follow=False, secure=False, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access_token", response.json())
        self.assertEqual(response.json()["expires_in"], 3600)
        self.assertEqual(response.json()["token_type"], "Bearer")
        self.assertEqual(response.json()["scope"], "blender.read blender.write")
