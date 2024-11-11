import uuid
from datetime import datetime, timedelta

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

import config

class Base(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=datetime.now(), nullable=True)


class Code(Base):
    __tablename__ = "code_table"

    email: Mapped[str]
    code: Mapped[str]
    expire_datetime: Mapped[datetime] = mapped_column(default=datetime.now() + timedelta(minutes=config.CODE_EXPIRES_IN_MINUTES)) # Срок годности


class User(Base):
    __tablename__ = "user_table"

    name: Mapped[str] # Имя
    surname: Mapped[str] # Фамилия

    email: Mapped[str] = mapped_column(nullable=True)

    surveys: Mapped[list["Survey"]] = relationship(back_populates="user")
    user_surveys: Mapped[list["UserSurveyResult"]] = relationship(back_populates="user")


class Survey(Base):
    __tablename__ = "survey_table"

    document: Mapped["SurveyDocument"] = relationship(uselist=False, backref="survey")

    user: Mapped["User"] = relationship(back_populates="surveys")
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_table.id", ondelete="SET NULL"))

    title: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)

    is_anonim: Mapped[bool] = mapped_column(default=False) # Режим анонимных отправок
    is_quiz: Mapped[bool] = mapped_column(default=False) # Режим квиза
    show_results: Mapped[bool] = mapped_column(default=False) # Режим показа результатов
    show_score: Mapped[bool] = mapped_column(default=False) # Режим показа баллов
    send_multiple_times: Mapped[bool] = mapped_column(default=False) # Режим отправки нескольких ответов

    is_finished: Mapped[bool] = mapped_column(default=False) # Завершен ли опрос
    expire_datetime: Mapped[datetime] = mapped_column(nullable=True) # Дата завершения

    questions: Mapped[list["Question"]] = relationship(back_populates="survey")
    user_survey_results: Mapped[list["UserSurveyResult"]] = relationship(back_populates="survey")


class Question(Base):
    __tablename__ = "question_table"

    survey: Mapped["Survey"] = relationship(back_populates="questions")
    survey_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("survey_table.id", ondelete="CASCADE"))

    title: Mapped[str]
    score: Mapped[int] = mapped_column(default=0)
    type: Mapped[ENUM] = mapped_column(ENUM("text", "choose_one", "choose_many", "dropdown_list", name="question_type_enum", create_type=False))
    is_required: Mapped[bool] = mapped_column(default=False) # Обязателен ли
    
    show_answers: Mapped[bool] = mapped_column(default=False)
    answers: Mapped[list["QuestionAnswer"]] = relationship(back_populates="question")
    user_question_results: Mapped[list["UserQuestionResult"]] = relationship(back_populates="question")


class QuestionAnswer(Base):
    __tablename__ = "question_answer_table"

    question: Mapped["Question"] = relationship(back_populates="answers")
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("question_table.id", ondelete="CASCADE"))

    is_correct: Mapped[bool] = mapped_column(default=False) # Правильный ли ответ

    text: Mapped[str]


class UserSurveyResult(Base):
    __tablename__ = "user_survey_result_table"

    user: Mapped["User"] = relationship(back_populates="user_surveys")
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_table.id", ondelete="SET NULL"), nullable=True)
    survey: Mapped["Survey"] = relationship(back_populates="user_survey_results")
    survey_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("survey_table.id", ondelete="CASCADE"))

    user_questions: Mapped[list["UserQuestionResult"]] = relationship(back_populates="user_survey_result")


class UserQuestionResult(Base):
    __tablename__ = "user_question_result_table"

    user_survey_result: Mapped["UserSurveyResult"] = relationship(back_populates="user_questions")
    user_survey_result_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_survey_result_table.id", ondelete="CASCADE"))
    question: Mapped["Question"] = relationship(back_populates="user_question_results")
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("question_table.id", ondelete="CASCADE"))

    user_answers: Mapped[list["UserAnswerResult"]] = relationship(back_populates="user_question_result")


class UserAnswerResult(Base):
    __tablename__ = "user_answer_result_table"

    user_question_result: Mapped["UserQuestionResult"] = relationship(back_populates="user_answers")
    user_question_result_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_question_result_table.id", ondelete="CASCADE"))

    is_correct: Mapped[bool] = mapped_column(default=False) # Правильный ли ответ
    
    text: Mapped[str]


class SurveyDocument(Base):
    __tablename__ = "survey_document_table"

    survey_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("survey_table.id", ondelete="CASCADE"))

    title: Mapped[str]
    refresh_document_datetime: Mapped[datetime] = mapped_column(
        default=datetime.now() + timedelta(minutes=config.WAIT_BEFORE_REFRESH_DOCUMENT_MINUTES),
        onupdate=datetime.now() + timedelta(minutes=config.WAIT_BEFORE_REFRESH_DOCUMENT_MINUTES)
    )

