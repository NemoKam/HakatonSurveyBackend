import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from fastapp import emails, crud, dependencies
from fastapp.database import sessionmanager
from fastapp.tasks.celeryconfig import celery_app

async def _delete_expired_codes():
    db: AsyncSession = sessionmanager.session_maker()
    await crud.delete_expired_codes(db)
    await sessionmanager.close()

async def _delete_codes_by_email(email: str):
    db: AsyncSession = sessionmanager.session_maker()
    await crud.delete_codes_by_email(db, email)
    await sessionmanager.close()

async def _refresh_survey_document(survey_document_id: uuid.UUID, survey_document_title: str):
    db: AsyncSession = sessionmanager.session_maker()
    await dependencies.refresh_survey_document(db, survey_document_id, survey_document_title)
    await sessionmanager.close()

@celery_app.task()
def send_mail(receiver_email: str, title: str, message: str):
    asyncio.run(emails.send_email(receiver_email, title, message))


@celery_app.task()
def delete_codes_by_email(email: str):
    asyncio.run(_delete_codes_by_email(email))


@celery_app.task()
def delete_expired_codes():
    asyncio.run(_delete_expired_codes())


@celery_app.task()
def refresh_survey_document(survey_document_id: uuid.UUID, survey_document_title: str):
    asyncio.run(_refresh_survey_document(survey_document_id, survey_document_title))