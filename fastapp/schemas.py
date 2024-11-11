from enum import Enum
from datetime import datetime
from pydantic import BaseModel, model_validator

import uuid

# Base Models
class BaseConfigModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        use_enum_values = True


class BaseCustomModel(BaseConfigModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime | None = None


# Code Schemas
class CodeBase(BaseConfigModel):
    email: str
    code: str


class CodeCreate(CodeBase):
    pass


# User Models
class UserBase(BaseConfigModel):
    name: str # Имя
    surname: str # Фамилия
    email: str | None = None


class UserCreate(UserBase):
    code: str


class UserLogin(BaseConfigModel):
    email: str
    code: str


class User(UserBase):
    pass

# Email
class Email(BaseConfigModel):
    email: str


# Jwt & Token Models
class JwtTokenGet(BaseConfigModel):
    token: str
    expire: datetime


class JwtTokenCreate(JwtTokenGet):
    payload: dict


class JwtToken(JwtTokenCreate):
    pass


class TokenPair(BaseConfigModel):
    access: JwtToken
    refresh: JwtToken


# Survey Models
class SurveyBase(BaseConfigModel):
    title: str
    description: str | None = None

    is_anonim: bool = False # Режим анонимных отправок
    is_quiz: bool = False # Режим квиза
    show_results: bool = False # Режим показа результатов
    show_score: bool = False # Режим показа баллов
    send_multiple_times: bool = False # Режим отправки нескольких ответов

    expire_datetime: datetime | None = None # Дата завершения


class SurveyCreate(SurveyBase):
    questions: list["QuestionCreate"]

class Survey(SurveyCreate, BaseCustomModel):
    user: "User"
    user_id: uuid.UUID
    is_finished: bool = False # Завершен ли опрос

class SurveyGet(Survey):
    questions: list["QuestionGet"]

    @model_validator(mode="after")
    def filter_answers_based_on_type(cls, survey):
        if not survey.show_results:
            for question in survey.questions:
                # Если `show_answers` у вопроса = False
                if not question.show_answers:
                    if question.type == QuestionTypeEnum.text:
                        question.answers = None
                    else:
                        if question.answers is not None:
                            # Убираем поле is_correct
                            question.answers = [
                                QuestionAnswerGet(
                                    **{k: v for k, v in answer.dict().items() if k != "is_correct"}
                                ) for answer in question.answers
                            ]
        
        return survey

class SurveyId(BaseConfigModel):
    survey_id: uuid.UUID

# Question Models
class QuestionTypeEnum(str, Enum):
    text = "text"
    choose_one = "choose_one"
    choose_many = "choose_many"
    dropdown_list = "dropdown_list"
    

class QuestionBase(BaseConfigModel):
    title: str
    score: int = 0
    type: QuestionTypeEnum
    is_required: bool = False # Обязателен ли
    
    show_answers: bool = False
    answers: list["QuestionAnswerCreate"]


class QuestionCreate(QuestionBase):
    pass

class Question(QuestionCreate, BaseCustomModel):
    pass

class QuestionGet(Question):
    answers: list["QuestionAnswerGet"]


# QuestionAnswer Models
class QuestionAnswerBase(BaseConfigModel):
    text: str

class QuestionAnswerCreate(QuestionAnswerBase):
    is_correct: bool = False # Правильный ли ответ

class QuestionAnswer(QuestionAnswerCreate, BaseCustomModel):
    pass

class QuestionAnswerGet(QuestionAnswer):
    pass


# UserSurveyResult Models
class UserSurveyResultBase(BaseConfigModel):
    survey_id: uuid.UUID

class UserSurveyResultCreate(UserSurveyResultBase):
    user_questions: list["UserQuestionsResultCreate"]

class UserSurveyResultGet(UserSurveyResultBase, BaseCustomModel):
    survey: "SurveyBase"
    user_id: uuid.UUID | None = None
    user_questions: list["UserQuestionsResultGet"]

    @model_validator(mode="after")
    def filter_answers_based_on_type(cls, survey):
        if not survey.survey.show_results:
            for user_question in survey.user_questions:
                if not user_question.question.show_answers:
                    if user_question.question.type == QuestionTypeEnum.text:
                        user_question.question.answers = None
                    else:
                        if user_question.question.answers is not None:
                            user_question.question.answers = [
                                QuestionAnswerGet(
                                    **{k: v for k, v in answer.dict().items() if k != "is_correct"}
                                ) for answer in user_question.question.answers
                            ]
        return survey

class UserSurveyResultId(BaseConfigModel):
    survey_result_id: uuid.UUID


# UserQuestionsResult Models
class UserQuestionsResultBase(BaseConfigModel):
    question_id: uuid.UUID

class UserQuestionsResultCreate(UserQuestionsResultBase):
    user_answers: list["UserAnswerResultCreate"]

class UserQuestionsResult(UserQuestionsResultBase, BaseCustomModel):
    user_survey_result_id: uuid.UUID

class UserQuestionsResultGet(UserQuestionsResult):
    question: "QuestionGet"
    user_answers: list["UserAnswerResultGet"]

# UserAnswerResult Models
class UserAnswerResultBase(BaseConfigModel):
    text: str

class UserAnswerResultCreate(UserAnswerResultBase):
    pass

class UserAnswerResult(UserAnswerResultCreate, BaseCustomModel):
    user_question_result_id: uuid.UUID

class UserAnswerResultGet(UserAnswerResult):
    is_correct: bool