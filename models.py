from database import *
from flask_security import UserMixin, RoleMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, Column, Integer, \
    String, ForeignKey, Date, DateTime, Text, LargeBinary, DDL, event


# Database Model
class Roles(Base, RoleMixin):
    __tablename__ = 'roles'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class Users(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    date = Column(Date(), nullable=False)

    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    active = Column(Boolean())
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    confirmed_at = Column(DateTime())

    roles = relationship('Roles', secondary='roles_users', backref=backref('users', lazy='dynamic'))
    forms_created = relationship('Forms')


# Tables for n to n relationship
class RolesUsers(Base):
    __tablename__ = 'roles_users'
    user_id = Column('user_id', Integer(), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column('role_id', Integer(), ForeignKey('roles.id'), primary_key=True)


# FORMS
class Forms(Base):
    __tablename__ = 'forms'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    dataCreation = Column(DateTime())
    description = Column(String(255))
    creator_id = Column(Integer, ForeignKey(Users.id, ondelete='CASCADE'), nullable=False)

    questions = relationship('Questions', secondary='forms_questions')
    answers = relationship('Answers', back_populates='form')


# Tables for n to n relationship
class FormsQuestions(Base):
    __tablename__ = 'forms_questions'
    form_id = Column('form_id', Integer(), ForeignKey('forms.id', ondelete='CASCADE'), primary_key=True)
    question_id = Column('question_id', Integer(), ForeignKey('questions.id'), primary_key=True)
    mandatory = Column('mandatory', Boolean(), default=False, nullable=False)
    has_file = Column(Boolean, default=False, nullable=False)


# QUESTIONS
class Questions(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)

    tags = relationship('Tags', secondary='tags_questions', back_populates='questions')
    answers = relationship('Answers', back_populates='question')
    multiple_choice = relationship('MultipleChoiceQuestions')
    single = relationship('SingleQuestions')
    open = relationship('OpenQuestions')


class SingleQuestions(Base):
    __tablename__ = 'single_questions'
    id = Column(Integer, ForeignKey(Questions.id), primary_key=True)

    possible_answers = relationship('PossibleAnswersS')


class PossibleAnswersS(Base):
    __tablename__ = 'possible_answers_s'
    idPosAnswS = Column(Integer, ForeignKey(SingleQuestions.id), primary_key=True)
    content = Column(String, primary_key=True)


class OpenQuestions(Base):
    __tablename__ = 'open_questions'
    id = Column(Integer, ForeignKey(Questions.id), primary_key=True)


class MultipleChoiceQuestions(Base):
    __tablename__ = 'multiple_choice_questions'
    id = Column(Integer, ForeignKey(Questions.id), primary_key=True)

    possible_answers = relationship('PossibleAnswersM')


class PossibleAnswersM(Base):
    __tablename__ = 'possible_answers_m'
    idPosAnswM = Column(Integer, ForeignKey(MultipleChoiceQuestions.id), primary_key=True)
    content = Column(String, primary_key=True)


# TAGS
class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    argument = Column(String(), unique=True, nullable=False)

    questions = relationship('Questions', secondary='tags_questions', back_populates='tags')


# Tables for n to n relationship
class TagsQuestions(Base):
    __tablename__ = 'tags_questions'
    tag_id = Column('tag_id', Integer(), ForeignKey('tags.id'), primary_key=True)
    question_id = Column('question_id', Integer(), ForeignKey('questions.id'), primary_key=True)


# ANSWERS
class Answers(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(Integer, ForeignKey(Forms.id, ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey(Questions.id, ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey(Users.id, ondelete='CASCADE'), nullable=False)

    question = relationship('Questions', back_populates='answers')
    text = relationship('SeqAnswers')
    form = relationship('Forms', back_populates='answers')
    user = relationship('Users')


class Files(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    data = Column(LargeBinary, nullable=False)
    name = Column(Text, nullable=False)
    mimetype = Column(Text, nullable=False)
    answer_id = Column(Integer, ForeignKey(Answers.id, ondelete='CASCADE'), nullable=False)


class SeqAnswers(Base):
    __tablename__ = 'seq_answers'
    id = Column(Integer, ForeignKey(Answers.id, ondelete='CASCADE'), primary_key=True)
    content = Column(Text, primary_key=True)


# Triggers in Plpgsql
only_one_answer_func = DDL(
    "CREATE FUNCTION only_one_answer_func() "
    "RETURNS TRIGGER AS $$ "
    "BEGIN "
    "IF (NEW.user_id, NEW.question_id) IN (SELECT user_id, question_id FROM answers WHERE form_id=NEW.form_id) THEN "
    "RETURN NULL; "
    "END IF; "
    "RETURN NEW; "
    "END; $$ LANGUAGE PLPGSQL;"
)

trigger_only_one_answer = DDL(
    "CREATE TRIGGER only_one_answer BEFORE INSERT ON answers "
    "FOR EACH ROW EXECUTE PROCEDURE only_one_answer_func();"
)

event.listen(
    Answers.__table__,
    'after_create',
    only_one_answer_func.execute_if(dialect='postgresql')
)

event.listen(
    Answers.__table__,
    'after_create',
    trigger_only_one_answer.execute_if(dialect='postgresql')
)

file_only_onOpenQuestion_func = DDL(
    "CREATE FUNCTION file_only_onOpenQuestion_func() "
    "RETURNS TRIGGER AS $$ "
    "BEGIN "
    "IF NEW.has_file AND ( (NEW.question_id IN (SELECT s.id FROM single_questions s)) OR "
    "(NEW.question_id IN (SELECT m.id FROM multiple_choice_questions m)) ) THEN "
    "RETURN NULL; "
    "END IF; "
    "RETURN NEW; "
    "END; $$ LANGUAGE PLPGSQL;"
)

trigger_only_onOpenQuestion = DDL(
    "CREATE TRIGGER only_onOpenQuestion BEFORE INSERT ON forms_questions "
    "FOR EACH ROW EXECUTE PROCEDURE file_only_onOpenQuestion_func();"
)

event.listen(
    FormsQuestions.__table__,
    'after_create',
    file_only_onOpenQuestion_func.execute_if(dialect='postgresql')
)

event.listen(
    FormsQuestions.__table__,
    'after_create',
    trigger_only_onOpenQuestion.execute_if(dialect='postgresql')
)



