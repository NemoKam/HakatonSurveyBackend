import datetime
import uuid

from sqlalchemy import insert, select, delete, update, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import _ColumnExpressionArgument

import config
from fastapp import models, dependencies, schemas, exceptions


# User

async def create_user(
    db: AsyncSession,
    user: schemas.UserCreate
) -> models.User:
    new_user: models.User = models.User(name=user.name, surname=user.surname, email=user.email)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def _get_user(
    db: AsyncSession,
    whereclause: _ColumnExpressionArgument[bool]
) -> models.User | None:
    select_user_stmt = select(models.User).where(whereclause)
    user: models.User = (await db.scalars(select_user_stmt)).one_or_none()

    return user


async def get_user_by_id(
    db: AsyncSession,
    user_id: uuid.UUID
) -> models.User | None:
    whereclause = (models.User.id == user_id)

    return await _get_user(db, whereclause)


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> models.User | None:
    whereclause = and_(
        models.User.email == email
    )

    return await _get_user(db, whereclause)


# Code

async def _get_code(
    db: AsyncSession,
    whereclause: _ColumnExpressionArgument[bool]
) -> models.Code | None:
    get_code_stmt = select(models.Code)

    get_code_stmt = get_code_stmt.where(whereclause)

    code: models.Code | None = (await db.scalars(get_code_stmt)).one_or_none()

    return code


async def _get_codes(
    db: AsyncSession,
    whereclause: _ColumnExpressionArgument[bool],
) -> list[models.Code]:
    get_code_stmt = select(models.Code)

    get_code_stmt = get_code_stmt.where(whereclause)

    codes: list[models.Code] = (await db.scalars(get_code_stmt)).all()

    return codes


async def get_code_by_user_email(
    db: AsyncSession,
    email: str
) -> models.Code | None:
    whereclause = and_(
        models.Code.email == email,
        models.Code.expire_datetime >= datetime.datetime.now()
    )

    return await _get_code(db, whereclause)

async def get_codes_by_user_email(
    db: AsyncSession,
    email: str
) -> list[models.Code]:
    whereclause = and_(
        models.Code.email == email,
        models.Code.expire_datetime >= datetime.datetime.now()
    )

    return await _get_codes(db, whereclause)


async def get_code_by_user_email_and_code(
    db: AsyncSession,
    email: str,
    code: str
) -> models.Code | None:
    whereclause = and_(
        models.Code.email == email,
        models.Code.code == code,
        models.Code.expire_datetime >= datetime.datetime.now()
    )

    return await _get_code(db, whereclause)


async def create_code(
    db: AsyncSession,
    email: str
) -> str:
    email_codes: list[models.Code] = await get_codes_by_user_email(db, email)
    if len(email_codes) < config.MAX_EXISTING_CODE_COUNT:
        code: str = dependencies.generate_random_string(config.VERIFICATION_CODE_LENGTH, config.VERIFICATION_CODE_ONLY_DIGITS)
        create_code_stmt = insert(models.Code).values(email=email, code=code, expire_datetime=datetime.datetime.now() + datetime.timedelta(minutes=config.CODE_EXPIRES_IN_MINUTES))

        await db.execute(create_code_stmt)
        await db.commit()

        return code
    else:
        raise exceptions.CodeMoreThanExisting()


async def _delete_code(
    db: AsyncSession,
    whereclause: _ColumnExpressionArgument[bool]
) -> None:
    delete_users_stmt = delete(models.Code).where(whereclause)

    await db.execute(delete_users_stmt)
    await db.commit()


async def delete_codes_by_email(
    db: AsyncSession,
    email: str
) -> None:
    whereclause = (
        models.Code.email == email
    )

    await _delete_code(db, whereclause)


async def delete_expired_codes(
    db: AsyncSession
) -> None:
    whereclause = (
        models.Code.expire_datetime < datetime.datetime.now()
    )

    return await _delete_code(db, whereclause)


# Survey

async def create_survey(
    db: AsyncSession,
    user_id: uuid.UUID,
    survey_schema: schemas.SurveyCreate
) -> uuid.UUID:
    insert_survey_stmt = insert(models.Survey).values(
        user_id=user_id, **survey_schema.model_dump(exclude={"questions"})
    ).returning(models.Survey.id)

    survey_model = await db.execute(insert_survey_stmt)
    survey_id: uuid.UUID = survey_model.scalar()

    question_schemas: list[schemas.QuestionCreate] = survey_schema.questions
    for question_schema in question_schemas:
        insert_question_stmt = insert(models.Question).values(
            survey_id=survey_id, **question_schema.model_dump(exclude={"answers"})
        ).returning(models.Question.id)

        question_model = await db.execute(insert_question_stmt)
        question_id: uuid.UUID = question_model.scalar()

        answer_schemas: list[schemas.QuestionAnswerCreate] = question_schema.answers
        for answer_schema in answer_schemas:
            insert_answer_stmt = insert(models.QuestionAnswer).values(
                question_id=question_id, **answer_schema.model_dump()
            )

            await db.execute(insert_answer_stmt)

    await db.commit()

    return survey_id


async def _get_surveys(
    db: AsyncSession,
    whereclause: _ColumnExpressionArgument[bool] | None = None,
    load_inner_models: bool = True,
    load_user_answers: bool = False,
    load_document_survey: bool = False,
    only_one: bool = False
) -> list[models.Survey] | models.Survey | None:
    select_surveys_stmt = select(models.Survey)

    if whereclause is not None:
        select_surveys_stmt = select_surveys_stmt.where(whereclause)
    
    if load_inner_models:
        select_surveys_stmt = select_surveys_stmt.options(
            selectinload(models.Survey.user),
            selectinload(models.Survey.questions).
            selectinload(models.Question.answers),
        ).options(
            selectinload(models.Survey.user_survey_results).
            selectinload(models.UserSurveyResult.survey)
        )

    if load_user_answers:
        select_surveys_stmt = select_surveys_stmt.options(
            selectinload(models.Survey.user_survey_results).
            selectinload(models.UserSurveyResult.user_questions).
            selectinload(models.UserQuestionResult.user_answers),
        ).options(
            selectinload(models.Survey.user_survey_results).
            selectinload(models.UserSurveyResult.user)
        ).options(
            selectinload(models.Survey.user_survey_results).
            selectinload(models.UserSurveyResult.user_questions).
            selectinload(models.UserQuestionResult.question)
        )
    if load_document_survey:
        select_surveys_stmt = select_surveys_stmt.options(
            selectinload(models.Survey.document)
        )

    if not only_one:
        surveys: list[models.Survey] = (await db.scalars(select_surveys_stmt)).all()
    else:
        surveys: models.Survey | None = (await db.scalars(select_surveys_stmt)).one_or_none()

    return surveys


async def get_surveys_by_user_id(
    db: AsyncSession,
    user_id: uuid.UUID
) -> list[models.Survey]:
    whereclause = (
        models.Survey.user_id == user_id
    )

    surveys: list[models.Survey] = await _get_surveys(db, whereclause)

    return surveys


async def get_survey_by_id(
    db: AsyncSession,
    survey_id: uuid.UUID,
    load_user_answers: bool = False,
    load_document_survey: bool = False
) -> models.Survey | None:
    whereclause = (
        models.Survey.id == survey_id
    )

    survey: models.Survey | None = await _get_surveys(db, whereclause, load_user_answers=load_user_answers, load_document_survey=load_document_survey, only_one=True)

    return survey


async def update_survey_expire_datetime_by_id(
    db: AsyncSession,
    survey_id: uuid.UUID,
    survey_expire_datetime: datetime.datetime
):
    update_survey_expire_datetime_stmt = update(models.Survey).where(
        models.Survey.id == survey_id
    ).values(
        expire_datetime=survey_expire_datetime
    )

    await db.execute(update_survey_expire_datetime_stmt)
    await db.commit()


# Survey Result

async def create_answer_for_survey(
    db: AsyncSession,
    user_id: uuid.UUID | None,
    survey_id: uuid.UUID,
    survey_result_create_schema: schemas.UserSurveyResultCreate
) -> uuid.UUID:
    survey: models.Survey = await get_survey_by_id(db, survey_id)

    if survey:
        required_question_ids: list[uuid.UUID] = [question.id for question in survey.questions if question.is_required]
        
        insert_survey_result_stmt = insert(models.UserSurveyResult).values(
            user_id=user_id, survey_id=survey_id
        ).returning(models.UserSurveyResult.id)

        survey_result = await db.execute(insert_survey_result_stmt)
        survey_result_id: uuid.UUID = survey_result.scalar()


        question_result_schemas: list[schemas.UserQuestionsResultCreate] = survey_result_create_schema.user_questions
        for question_result_schema in question_result_schemas:
            insert_question_result_stmt = insert(models.UserQuestionResult).values(
                user_survey_result_id=survey_result_id, **question_result_schema.model_dump(exclude={"user_answers"})
            ).returning(models.UserQuestionResult.id)

            question_result_model = await db.execute(insert_question_result_stmt)
            question_result_id: uuid.UUID = question_result_model.scalar()

            has_at_least_one_non_empty_answer = False

            answer_result_schemas: list[schemas.UserAnswerResultCreate] = question_result_schema.user_answers
            for answer_result_schema in answer_result_schemas:
                insert_answer_stmt = insert(models.UserAnswerResult).values(
                    user_question_result_id=question_result_id, **answer_result_schema.model_dump()
                )

                if answer_result_schema.text != "":
                    has_at_least_one_non_empty_answer = True

                await db.execute(insert_answer_stmt)
            
            if has_at_least_one_non_empty_answer:
                try:
                    required_question_ids.remove(question_result_schema.question_id)
                except ValueError:
                    pass

        if len(required_question_ids) == 0: # Has answer for all required questions
            await db.commit()

            return survey_result_id
        else:
            string_required_question_ids: list[str] = [str(required_question_id) for required_question_id in required_question_ids]
            raise exceptions.BadRequestException(detail="Not answered to this questions: " + ",".join(string_required_question_ids))


async def _get_survey_results(
    db: AsyncSession,
    whereclause: _ColumnExpressionArgument[bool] | None = None,
    load_inner_models: bool = True
) -> list[models.UserSurveyResult]:
    select_survey_results_stmt = select(models.UserSurveyResult)

    if whereclause is not None:
        select_survey_results_stmt = select_survey_results_stmt.where(whereclause)

    if load_inner_models:
        select_survey_results_stmt = select_survey_results_stmt.options(
            selectinload(models.UserSurveyResult.survey)
        )
        select_survey_results_stmt = select_survey_results_stmt.options(
            selectinload(models.UserSurveyResult.user_questions).
            selectinload(models.UserQuestionResult.user_answers)
        )
        select_survey_results_stmt = select_survey_results_stmt.options(
            selectinload(models.UserSurveyResult.user_questions).
            selectinload(models.UserQuestionResult.question).
            selectinload(models.Question.answers)
        )

    survey_results: list[models.UserSurveyResult] = (await db.scalars(select_survey_results_stmt)).all()

    return survey_results


async def get_survey_results_by_user_id(
    db: AsyncSession,
    user_id: uuid.UUID
) -> list[models.UserSurveyResult]:
    whereclause = (
        models.UserSurveyResult.user_id == user_id
    )

    return await _get_survey_results(db, whereclause)


# Survey Document

async def create_survey_document(
    db: AsyncSession,
    survey_id: uuid.UUID,
    title: str
) -> uuid.UUID:
    insert_survey_document_stmt = insert(models.SurveyDocument).values(
        survey_id=survey_id, title=title
    ).returning(models.SurveyDocument.id)

    return_survey_document_model = await db.execute(insert_survey_document_stmt)
    survey_document_id: uuid.UUID = return_survey_document_model.scalar()

    await db.commit()

    return survey_document_id


async def _get_survey_document(
    db: AsyncSession,
    whereclause: _ColumnExpressionArgument[bool] | None = None
) -> models.SurveyDocument | None:
    select_survey_document_stmt = select(models.SurveyDocument)

    if whereclause is not None:
        select_survey_document_stmt = select_survey_document_stmt.where(whereclause)

    survey_document: models.SurveyDocument | None = await db.scalar(select_survey_document_stmt)

    return survey_document


async def get_survey_document_by_survey_id(
    db: AsyncSession,
    survey_id: uuid.UUID
) -> models.SurveyDocument | None:
    whereclause = (
        models.SurveyDocument.survey_id == survey_id
    )

    survey_document: models.SurveyDocument | None = await _get_survey_document(db, whereclause)

    return survey_document


async def get_survey_document_by_id(
    db: AsyncSession,
    survey_document_id: uuid.UUID
) -> models.SurveyDocument | None:
    whereclause = (
        models.SurveyDocument.id == survey_document_id
    )

    survey_document: models.SurveyDocument | None = await _get_survey_document(db, whereclause)

    return survey_document


async def update_survey_document_refresh_datetime_by_id(
    db: AsyncSession,
    survey_document_id: uuid.UUID
):
    update_survey_document_stmt = update(models.SurveyDocument).where(
        models.SurveyDocument.id == survey_document_id
    )

    await db.execute(update_survey_document_stmt)
    await db.commit()
