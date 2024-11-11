import os

from dotenv import load_dotenv

load_dotenv(override=True)

# PROJECT
PROJECT_TITLE = os.environ.get("PROJECT_TITLE")
PROJECT_HOST = os.environ.get("PROJECT_HOST")
PROJECT_PORT = int(os.environ.get("PROJECT_PORT"))

# DATABASE
DATABASE_USER = os.environ.get("DATABASE_USER")
DATABASE_PASSWORD  = os.environ.get("DATABASE_PASSWORD")
DATABASE_HOST = os.environ.get("DATABASE_HOST")
DATABASE_PORT = int(os.environ.get("DATABASE_PORT"))
DATABASE_NAME = os.environ.get("DATABASE_NAME")
TEST_DATABASE_NAME = os.environ.get("TEST_DATABASE_NAME")

# EMAIL
EMAIL_LOGIN = os.environ.get("EMAIL_LOGIN")
EMAIL_SMTP_HOST = os.environ.get("EMAIL_SMTP_HOST")
EMAIL_SMTP_PORT = int(os.environ.get("EMAIL_SMTP_PORT"))
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# CELERY 
CELERY_WORKER_COUNT = 1
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_BACKEND_URL = os.environ.get("CELERY_BACKEND_URL")

# CODE
CODE_EXPIRES_IN_MINUTES = int(os.environ.get("CODE_EXPIRES_IN_MINUTES"))
MAX_EXISTING_CODE_COUNT = int(os.environ.get("MAX_EXISTING_CODE_COUNT"))
VERIFICATION_CODE_LENGTH = int(os.environ.get("VERIFICATION_CODE_LENGTH"))
VERIFICATION_CODE_ONLY_DIGITS = (os.environ.get("VERIFICATION_CODE_ONLY_DIGITS")  ==  "True")

# SURVEY DOCUMENT
WAIT_BEFORE_REFRESH_DOCUMENT_MINUTES = 30
SURVEY_DOCUMENT_SAVE_PATH="fastapp/media/survey_documents/"

# JWT
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRES_MINUTES = 15 * 8 # 2 hours
REFRESH_TOKEN_EXPIRES_MINUTES = 15 * 24 * 60  # 15 days
REFRESH_COOKIE_NAME = "refresh"
SUB = "sub"
EXP = "exp"
IAT = "iat"
JTI = "jti"