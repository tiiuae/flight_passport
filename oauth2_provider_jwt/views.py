import ast
import json
import logging
import os
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.http import HttpResponse
from django.utils.module_loading import import_string
from jwcrypto import jwk
from oauth2_provider import views
from oauth2_provider.http import OAuth2ResponseRedirect
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status

from oauth2_provider_jwt import utils

# Create your views here.


logger = logging.getLogger(__name__)


class MissingIdAttribute(Exception):
    pass


class IncorrectAudience(Exception):
    pass


class InvalidUUID(Exception):
    pass


class JWTAuthorizationView(views.AuthorizationView):
    def get(self, request, *args, **kwargs):
        response = super(JWTAuthorizationView, self).get(request, *args, **kwargs)

        if request.GET.get("response_type", None) == "token" and response.status_code == 302:
            url = urlparse(response.url)
            params = parse_qs(url.fragment)

            if params:
                content = {
                    "access_token": params["access_token"][0],
                    "expires_in": int(params["expires_in"][0]),
                    "scope": params["scope"][0],
                }
                jwt = TokenView()._get_access_token_jwt(request, content)

                response = OAuth2ResponseRedirect("{}&access_token_jwt={}".format(response.url, jwt), response.allowed_schemes)
        return response


class TokenView(views.TokenView):
    def _get_access_token_jwt(self, request, content):
        extra_data = {}

        issuer = settings.JWT_ISSUER_DOMAIN
        payload_enricher = getattr(settings, "JWT_PAYLOAD_ENRICHER", None)
        request_params = list(request.POST.keys())

        token = AccessToken.objects.get(token=content["access_token"])
        if payload_enricher:
            fn = import_string(payload_enricher)
            extra_data = fn(request)

        if "scope" in content:
            extra_data["scope"] = content["scope"].split()
            extra_data["typ"] = "Bearer"

        if "audience" in request_params:
            requested_audience = request.POST["audience"]
            audience_query = token.application.audience.all().only("identifier")
            all_audience = [audience.identifier for audience in audience_query]
            try:
                assert requested_audience in all_audience
            except AssertionError:
                raise IncorrectAudience()

            extra_data["aud"] = requested_audience

        if "flight_plan_id" in request_params:
            flight_plan_id = request.POST["flight_plan_id"]
            extra_data["flight_plan_id"] = flight_plan_id

        if "flight_operation_id" in request_params:
            flight_operation_id = request.POST["flight_operation_id"]
            extra_data["flight_operation_id"] = flight_operation_id

        if "plan_file_hash" in request_params:
            plan_file_hash = request.POST["plan_file_hash"]
            extra_data["plan_file_hash"] = plan_file_hash

        id_attribute = getattr(settings, "JWT_ID_ATTRIBUTE", None)

        if id_attribute:
            token_user = token.user
            try:
                assert token_user is not None
                id_value = getattr(token_user, id_attribute, None)
                if not id_value:
                    raise MissingIdAttribute()
            except AssertionError:
                id_value = token.application.client_id + "@clients"

            extra_data["sub"] = str(id_value)

        # Generate scopes for UUID
        if "client_uuid" in request_params:
            client_uuid = request.POST["client_uuid"]
            is_valid_uuid = utils.validate_uuid(client_uuid)
            if not is_valid_uuid:
                raise InvalidUUID()

            current_scope = extra_data.get("scope", [])
            rabbitmq_audience = os.environ.get("RABBITMQ_SERVER_AUDIENCE", "")
            if rabbitmq_audience:
                uuid_based_read_scope = f"{rabbitmq_audience}.read:*/{client_uuid}_*/*"
                uuid_based_configure_scope = f"{rabbitmq_audience}.configure:*/{client_uuid}_*"
                extra_data["scope"] = current_scope + [uuid_based_read_scope, uuid_based_configure_scope]

            current_audience = extra_data.get("aud", "")
            extra_data["audience"] = [aud for aud in [current_audience, rabbitmq_audience] if aud]
        payload = utils.generate_payload(issuer, content["expires_in"], **extra_data)

        if oauth2_settings.OIDC_RSA_PRIVATE_KEY:
            private_key_pem = str(oauth2_settings.OIDC_RSA_PRIVATE_KEY).encode("utf8")
            key = jwk.JWK.from_pem(private_key_pem)
            kid = key.thumbprint()

        else:
            kid = "e28163ce-b86d-4145-8df3-c8dad2e0b601"

        headers = {"kid": kid}

        token = utils.encode_jwt(payload, headers=headers)

        return token

    @staticmethod
    def _is_jwt_config_set():
        issuer = getattr(settings, "JWT_ISSUER", "")
        private_key_name = "JWT_PRIVATE_KEY_{}".format(issuer.upper())
        private_key = getattr(settings, private_key_name, None)
        id_attribute = getattr(settings, "JWT_ID_ATTRIBUTE", None)
        if issuer and private_key and id_attribute:
            return True
        else:
            return False

    def post(self, request, *args, **kwargs) -> HttpResponse:
        response = super(TokenView, self).post(request, *args, **kwargs)

        content = ast.literal_eval(response.content.decode("utf-8"))
        request.POST.get("grant_type")
        # Per the ASTM standards on UTM only the 'client_credentials' grant must be a JWT

        if response.status_code != status.HTTP_200_OK and "access_token" not in content:
            logger.error("Error in token generation")
            return response

        if not TokenView._is_jwt_config_set():
            logger.warning("Missing JWT configuration, skipping token build")
            return response

        try:
            token_raw = self._get_access_token_jwt(request=request, content=content)
            if not isinstance(token_raw, str):
                token_raw = token_raw.decode("utf-8")
            content["access_token"] = token_raw

        except MissingIdAttribute:
            error_message = json.dumps(
                {
                    "error": "invalid_request",
                    "error_description": "App not configured correctly. " "Please set JWT_ID_ATTRIBUTE.",
                }
            )
            return HttpResponse(
                json.dumps(error_message),
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        except IncorrectAudience:
            error_message = json.dumps(
                {
                    "error": "invalid_request",
                    "error_description": "Incorrect Audience. " "Please set the appropriate audience in the request.",
                }
            )
            return HttpResponse(
                json.dumps(error_message),
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        except InvalidUUID:
            error_message = json.dumps(
                {
                    "error": "invalid_request",
                    "error_description": "Invalid UUID. Please set the appropriate UUID in the request.",
                }
            )
            return HttpResponse(
                json.dumps(error_message),
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        except Exception:
            error_message = json.dumps(
                {
                    "error": "unhandled_server_exception",
                    "error_description": "Unhandled server exception. Please contact the server administrator.",
                }
            )
            return HttpResponse(
                json.dumps(error_message),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content_type="application/json",
            )
        content = json.dumps(content)

        return HttpResponse(content, status=response.status_code, content_type="application/json")
