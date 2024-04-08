from os import environ as env

import tldextract
from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError
from dotenv import find_dotenv, load_dotenv

from . import constants

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


class PassportAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        DOMAIN_WHITELIST = env.get(constants.DOMAIN_WHITELIST)
        domain = email.split("@")[1]
        white_listed_domain = [i for i in DOMAIN_WHITELIST.split(";")]

        if domain in white_listed_domain:
            ext = tldextract.extract(domain)
            ext.domain.upper()
            ext.suffix.upper()
            return email
        else:
            raise ValidationError("You are restricted from registering. Please contact admin.")
