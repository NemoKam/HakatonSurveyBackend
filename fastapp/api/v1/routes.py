import uuid
import datetime

from fastapi import APIRouter, Query, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

import config
from fastapp.database import get_db
from fastapp.tasks import celery_tasks
from fastapp import dependencies, exceptions, schemas, crud, models

router = APIRouter(prefix="/v1", tags=["v1"])


@router.get("/survey", response_model=list[schemas.SurveyGet])
async def get_my_surveys(user: models.User = Depends(dependencies.get_user_from_access_token), db: AsyncSession = Depends(get_db)) -> JSONResponse:
    surveys: list[models.Survey] = await crud.get_surveys_by_user_id(db, user.id)
    
    return surveys


@router.get("/survey/passed", response_model=list[schemas.UserSurveyResultGet])
async def get_my_surveys(user: models.User = Depends(dependencies.get_user_from_access_token), db: AsyncSession = Depends(get_db)) -> JSONResponse:
    surveys: list[models.UserSurveyResult] = await crud.get_survey_results_by_user_id(db, user.id)

    return surveys


@router.post("/survey/create", response_model=schemas.SurveyId)
async def create_survey(survey_schema: schemas.SurveyCreate, user: models.User = Depends(dependencies.get_user_from_access_token), db: AsyncSession = Depends(get_db)) -> JSONResponse:
    survey_id = await crud.create_survey(db, user.id, survey_schema)

    survey_id_schema = schemas.SurveyId(survey_id=survey_id)
    
    return survey_id_schema


@router.get("/survey/{survey_id}/", response_model=schemas.SurveyGet)
async def get_survey_by_id(survey_id: uuid.UUID, authorization: str | None = Header(None), db: AsyncSession = Depends(get_db)) -> JSONResponse:
    survey: models.Survey | None = await crud.get_survey_by_id(db, survey_id, load_user_answers=True)
    
    await dependencies.check_survey_is_valid(db, survey, authorization)

    return survey


@router.get("/survey/{survey_id}/answer", response_model=list[schemas.UserSurveyResultGet])
async def get_answers_for_survey(survey_id: uuid.UUID, user: models.User = Depends(dependencies.get_user_from_access_token), db: AsyncSession = Depends(get_db)) -> JSONResponse:
    survey: models.Survey = await crud.get_survey_by_id(db, survey_id, load_user_answers=True)

    if survey.user_id != user.id:
        raise exceptions.NotAllowedException(detail="You are not the creator of this survey")
    
    user_servey_results: list[models.UserSurveyResult] = survey.user_survey_results

    return user_servey_results


@router.post("/survey/{survey_id}/answer", response_model=schemas.UserSurveyResultId)
async def send_answer_for_survey(survey_id: uuid.UUID, survey_result_create_schema: schemas.UserSurveyResultCreate, authorization: str | None = Header(None), db: AsyncSession = Depends(get_db)) -> JSONResponse:
    user: models.User | None = None
    user_id: uuid.UUID | None = None
    survey: models.Survey = await crud.get_survey_by_id(db, survey_id, load_user_answers=True)
    
    await dependencies.check_survey_is_valid(db, survey, authorization)
    
    if user:
        user_id: uuid.UUID = user.id

    survey_result_id: uuid.UUID = await crud.create_answer_for_survey(db, user_id, survey_id, survey_result_create_schema)

    survey_result_id_schema = schemas.UserSurveyResultId(survey_result_id=survey_result_id)

    return survey_result_id_schema


@router.post("/survey/{survey_id}/document/refresh")
async def refresh_survey_document(survey_id: uuid.UUID, user: models.User = Depends(dependencies.get_user_from_access_token), db: AsyncSession = Depends(get_db)) -> JSONResponse:
    survey: models.Survey = await crud.get_survey_by_id(db, survey_id, load_user_answers=True)
   
    if survey.user_id != user.id:
        raise exceptions.NotAllowedException(detail="You are not the creator of this survey")
    
    survey_document: models.SurveyDocument | None = await crud.get_survey_document_by_survey_id(db, survey_id)

    survey_document_title: str = f"{survey_id}"
    if survey_document is None:
        survey_document_id: uuid.UUID = await crud.create_survey_document(db, survey_id, title=survey_document_title)
        celery_tasks.refresh_survey_document.delay(survey_document_id, survey_document_title)
        
        return {"status": "success"}
    
    elif survey_document.refresh_document_datetime < datetime.datetime.now():
        survey_document_id: uuid.UUID = survey_document.id
        celery_tasks.refresh_survey_document.delay(survey_document_id, survey_document_title)
        await crud.update_survey_document_refresh_datetime_by_id(db, survey_document_id)

        return {"status": "success"}
    else:
        raise exceptions.BadRequestException(detail="Wait before refreshing document")


@router.get("/survey/{survey_id}/document/download")
async def download_survey_document(survey_id: uuid.UUID, user: models.User = Depends(dependencies.get_user_from_access_token), db: AsyncSession = Depends(get_db)) -> FileResponse:
    survey: models.Survey = await crud.get_survey_by_id(db, survey_id, load_user_answers=True, load_document_survey=True)
    
    if survey.user_id != user.id:
        raise exceptions.NotAllowedException(detail="You are not the creator of this survey")

    survey_document_filename: str = survey.document.title
    survey_document_path: str = f"{config.SURVEY_DOCUMENT_SAVE_PATH}/{survey_document_filename}.xlsx"

    return FileResponse(path=survey_document_path, filename=survey_document_filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.post("/survey/{survey_id}/finish")
async def finish_survey(survey_id: uuid.UUID, user: models.User = Depends(dependencies.get_user_from_access_token), db: AsyncSession = Depends(get_db)) -> JSONResponse:
    survey: models.Survey = await crud.get_survey_by_id(db, survey_id, load_user_answers=True, load_document_survey=True)
    
    if survey.user_id != user.id:
        raise exceptions.NotAllowedException(detail="You are not the creator of this survey")

    survey_expire_datetime = datetime.datetime.now()

    await crud.update_survey_expire_datetime_by_id(db, survey_id, survey_expire_datetime)

    return {"status": "success"}