import math
from .secrets import (
    MATHPIX_API_APP, MATHPIX_API_KEY, 
    AWS_SECRET_KEY, AWS_ACCESS_KEY, SENDGRID_API_KEY, SMTP_EMAIL, SMTP_PASSWORD, SMTP_PORT, SMTP_SERVER,
    CLERK_JWT_PEM, CLERK_SECRET_KEY, CUSTOM_AUTH_SECRET, CUSTOM_AUTH_DB_ENDPOINT, CUSTOM_AUTH_DB_USERNAME,
    CUSTOM_AUTH_DB_PASSWORD, CUSTOM_AUTH_DB_PORT, CUSTOM_AUTH_DB_NAME,
)
from .settings import SETTINGS
from ..integrations.lm import make_code_from_setting
from ..integrations.tts import TTS_PROVIDERS
from ..integrations.web import SEARCH_PROVIDERS
import os

BACKEND_VERSION = '0.12.7'  # Viewable when a user goes to the root "/" endpoint of the backend

AVAILABLE_TEMPLATES = ['document', 'folder', 'detached_chat', 'website', 'classroom', 'curriculum', 'quiz', 'text_editor', 'video', 'notebook', 'inf_quiz', 'section']  # could use the list in templates.py, but want to avoid imports here.

# This extra ranking is done so that a user sees a consistent / sensible ordering of LM options
LM_ORDER = [make_code_from_setting(x) for x in SETTINGS['lms']['models']]  # Order that a user would see in settings or a dropdown

APP_NAME = "Abbey"  # Used in certain prompts

#
# Subscription stuff
#

DEFAULT_SUBSCRIPTION_CODE = 'free'  # For users that don't have any subscription entries in their user metadata

# Options for user-selected chat models by subscription
SUBSCRIPTION_CODE_TO_MODEL_OPTIONS = {DEFAULT_SUBSCRIPTION_CODE: LM_ORDER, 'abbey-cathedral': LM_ORDER}
SUBSCRIPTION_CODE_TO_TEMPLATES = {DEFAULT_SUBSCRIPTION_CODE: AVAILABLE_TEMPLATES, 'abbey-cathedral': AVAILABLE_TEMPLATES}
SUBSCRIPTION_CODE_TO_SEARCH_OPTIONS = {DEFAULT_SUBSCRIPTION_CODE: [x.code for x in SEARCH_PROVIDERS.values()], 'abbey-cathedral': [x.code for x in SEARCH_PROVIDERS.values()]}
SUBSCRIPTION_CODE_TO_TOTAL_ASSET_LIMITS = {DEFAULT_SUBSCRIPTION_CODE: math.inf, 'abbey-cathedral': math.inf}
SUBSCRIPTION_CODE_TO_TTS_OPTIONS = {DEFAULT_SUBSCRIPTION_CODE: [x.code for x in TTS_PROVIDERS.values()], 'abbey-cathedral': [x.code for x in TTS_PROVIDERS.values()]}
if 'subscriptions' in SETTINGS:
    sub_code = SETTINGS['subscriptions']
    # TODO

# Options for optical-character-recognition by subscription tier
# Note that the frontend does not currently exist to allow a user to actually select one, so everyone is on the default
# However, in the future this could be user selected – once there are more options available.
DISABLE_OCR = not (MATHPIX_API_APP and MATHPIX_API_KEY)  # If true, OCR is disabled, which means that DisabledOCR ('disabled') is used for all users (and it accepts nothing, does nothing).
DEFAULT_OCR_OPTION = 'mathpix'  # codes match integrations/ocr.py

DEFAULT_STORAGE_OPTION = "s3" if AWS_ACCESS_KEY and AWS_SECRET_KEY else "local"  # codes match integrations/file_storage.py

DEFAULT_EMAIL_SERVICE = 'sendgrid' if SENDGRID_API_KEY else 'smtp'  # codes match integrations/email.py
EMAIL_FROM_NAME = "Abbey"  # The author of auto-generated emails
EMAIL_FROM_ADDRESS = os.environ.get('SENDGRID_EMAIL') if DEFAULT_EMAIL_SERVICE == 'sendgrid' else SMTP_EMAIL  # The address from which auto-generated emails are sent
SENDGRID_UNSUB_GROUP = int(os.environ.get('SENDGRID_UNSUB_GROUP')) if os.environ.get('SENDGRID_UNSUB_GROUP') else ""
DISABLE_EMAILS = not (SENDGRID_API_KEY or (SMTP_EMAIL and SMTP_PASSWORD and SMTP_PORT and SMTP_SERVER))

AUTH_SYSTEM = "clerk" if CLERK_SECRET_KEY and CLERK_JWT_PEM else "custom"
CUSTOM_AUTH_USE_DATABASE = True if (CUSTOM_AUTH_SECRET and CUSTOM_AUTH_DB_ENDPOINT and CUSTOM_AUTH_DB_USERNAME and CUSTOM_AUTH_DB_PASSWORD and CUSTOM_AUTH_DB_PORT and CUSTOM_AUTH_DB_NAME) else False

#
#  Mid-Importance Configuration Options
#

MAX_PDF_PAGES = 250  # SHOULD MATCH FRONTEND - the maximum size of a PDF a user can upload.

MAX_CHAT_RETRIEVER_RESULTS = 7  # When a retriever query is made (without max chunks, or when the full context won't fit in the model), this gives the maximum number of chunks that the query will return in most circumstances. 

RETRIEVER_JOB_TIMEOUT = 30  # in minutes, the max time we'll wait for a retriever to be created (e.g., a document to be processed)

# Domains a user cannot give permissions to on an asset (a user can share with someone@gmail.com, but not all users with a gmail.com email domain – but can give permissions to everyone with a us.ai domain name, or a superspecial.com domain name email.)
ILLEGAL_SHARE_DOMAINS = [
    'gmail.com',
    'hotmail.com',
    'me.com',
    'outlook.com',
    'aol.com',
    'yahoo.com',
    'hotmail.co.uk',
    'msn.com',
    'concast.net',
    'optonline.net'
]

MAX_EMAIL_LIMIT = 500  # The max number of recipients in a single email.
MAX_EMAIL_WAIT = 10  # The number of seconds that needs to go by after a previous email to send a user-action generated email

# The backend process communicates with redis as a message passer; this code configures that connection.
# Note that it uses both the redis protocol (not HTTP) as well as "redis" instead of localhost (due to docker compose)
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
CELERY_BROKER_URL = "redis://redis:6379/0"
POOLER_CONNECTION_PARAMS = {
    'host': 'redis',
    'port': 6379,
    'db': 1,  # Note that this is different from 0, the one used above for celery.
}

#
#  Least Important Configuration Options
#

DEFAULT_PRODUCT_ID = os.environ.get('DEFAULT_PRODUCT_ID')

# Controls whether actual permissioning applies or everyone is allowed to see everything
PERMISSIONING = "real"  # "real" | "demo"

# If someone isn't logged in (such as for a demo)
# we can allow users to edit certain templates
OVERRIDE_ALLOWED_TEMPLATES = []  # None | ['temp1', 'temp2']

# Allows users to make an asset available to those without an account / all accounts.
ALLOW_PUBLIC_UPLOAD = True  # NOTE: Should match frontend

#
# For the backend as called by a mobile app frontend
#

MOBILE_FRIENDLY_TEMPLATES = ['document', 'folder', 'detached_chat']  # controls whether these templates show up for mobile users in some backend calls

