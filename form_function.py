from functools import wraps

from flask import render_template
from flask_login import current_user
from sqlalchemy import false, and_, text, select

from models import *
from datetime import datetime


# DECORATORS
# checking if the current_user is an admin or the form creator
def creator_or_admin_role_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        form_id = kwargs.get('form_id')
        admin_role = db_session.query(Roles).filter(Roles.name == "Admin").first()
        creator = db_session.query(Forms).filter(and_(Forms.creator_id == current_user.id, Forms.id == form_id)).first()
        if not creator and admin_role not in current_user.roles:
            return render_template("error.html", message="You do not have permission to view that page")

        return f(*args, **kwargs)

    return decorated_function


# Checking if the current_user is an admin
def admin_role_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_role = db_session.query(Roles).filter(Roles.name == "Admin").first()
        if admin_role not in current_user.roles:
            return render_template("error.html", message="You do not have permission to view that page")

        return f(*args, **kwargs)

    return decorated_function


# Checking if the current_user is the superuser
def superuser_role_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_role = db_session.query(Roles).filter(Roles.name == "SuperUser").first()
        if admin_role not in current_user.roles:
            return render_template("error.html", message="You do not have permission to view that page")

        return f(*args, **kwargs)

    return decorated_function


# FUNCTIONS
# Base tags
def populate_tags():
    db_session.add_all([Tags(argument="Informazioni personali"),
                        Tags(argument="Organizzazione"),
                        Tags(argument="Altro"),
                        Tags(argument="Scuola"),
                        Tags(argument="Lavoro"),
                        Tags(argument="Animali"),
                        Tags(argument="Scienza"),
                        Tags(argument="Viaggio"),
                        Tags(argument="Ambiente"),
                        Tags(argument="Sondaggi")])
    db_session.commit()


# Base questions
def init_base_question():
    db_session.add_all([Questions(text="Nome"),  # 1
                        Questions(text="Cognome"),
                        Questions(text="Data Nascita"),
                        Questions(text="Età"),
                        Questions(text="Fascia d'età"),  # 5
                        Questions(text="Lavoro"),
                        Questions(text="Sesso"),
                        Questions(text="Mail"),
                        Questions(text="Paese di residenza"),
                        Questions(text="Via residenza"),  # 10
                        Questions(text="Inserisci l'orario che preferisci"),
                        Questions(text="Inserisci una data che preferisci"),
                        Questions(text="In quanti parteciperete?"),
                        Questions(text="Inserisci il giorno che preferisci"),
                        Questions(text="Scegli i giorni della settimana che preferisci"),  # 15
                        Questions(text="Parteciperai all'evento?"),
                        Questions(text="Inserisci un breve commento"),
                        Questions(text="Valuta questo sondaggio"),
                        Questions(text="Come hai conosciuto questo evento?"),
                        Questions(text="Hai intolleranze alimentari, se si quali?"),  # 20
                        Questions(text="Che corsi hai seguito? "),
                        Questions(text="Che materie studi?"),
                        Questions(text="Fai la raccolta differenziata?"),
                        Questions(text="Quali stati hai visitato?"),
                        Questions(text="Possiedi animali?"),  # 25
                        Questions(text="Animale preferito"),
                        Questions(text="Carica il tuo CV")])
    db_session.commit()

    db_session.add_all([OpenQuestions(id=1),
                        OpenQuestions(id=2),
                        OpenQuestions(id=3),
                        OpenQuestions(id=4),
                        SingleQuestions(id=5),
                        OpenQuestions(id=6),
                        SingleQuestions(id=7),
                        OpenQuestions(id=8),
                        OpenQuestions(id=9),
                        OpenQuestions(id=10),
                        OpenQuestions(id=11),
                        OpenQuestions(id=12),
                        OpenQuestions(id=13),
                        OpenQuestions(id=14),
                        MultipleChoiceQuestions(id=15),
                        SingleQuestions(id=16),
                        OpenQuestions(id=17),
                        SingleQuestions(id=18),
                        OpenQuestions(id=19),
                        OpenQuestions(id=20),
                        OpenQuestions(id=21),
                        OpenQuestions(id=22),
                        SingleQuestions(id=23),
                        OpenQuestions(id=24),
                        OpenQuestions(id=25),
                        OpenQuestions(id=26),
                        OpenQuestions(id=27),

                        TagsQuestions(tag_id=1, question_id=1),
                        TagsQuestions(tag_id=1, question_id=2),
                        TagsQuestions(tag_id=1, question_id=3),
                        TagsQuestions(tag_id=1, question_id=4),
                        TagsQuestions(tag_id=1, question_id=5),
                        TagsQuestions(tag_id=1, question_id=6),
                        TagsQuestions(tag_id=5, question_id=6),
                        TagsQuestions(tag_id=1, question_id=7),
                        TagsQuestions(tag_id=1, question_id=8),
                        TagsQuestions(tag_id=1, question_id=9),
                        TagsQuestions(tag_id=1, question_id=10),
                        TagsQuestions(tag_id=2, question_id=11),
                        TagsQuestions(tag_id=2, question_id=12),
                        TagsQuestions(tag_id=2, question_id=13),
                        TagsQuestions(tag_id=2, question_id=14),
                        TagsQuestions(tag_id=2, question_id=15),
                        TagsQuestions(tag_id=3, question_id=16),
                        TagsQuestions(tag_id=3, question_id=17),
                        TagsQuestions(tag_id=3, question_id=18),
                        TagsQuestions(tag_id=10, question_id=19),
                        TagsQuestions(tag_id=2, question_id=20),
                        TagsQuestions(tag_id=4, question_id=21),
                        TagsQuestions(tag_id=4, question_id=22),
                        TagsQuestions(tag_id=9, question_id=23),
                        TagsQuestions(tag_id=8, question_id=24),
                        TagsQuestions(tag_id=6, question_id=25),
                        TagsQuestions(tag_id=1, question_id=25),
                        TagsQuestions(tag_id=6, question_id=26),
                        TagsQuestions(tag_id=5, question_id=27)])
    db_session.commit()

    db_session.add_all([PossibleAnswersS(idPosAnswS=5, content="0-17"),
                        PossibleAnswersS(idPosAnswS=5, content="18-21"),
                        PossibleAnswersS(idPosAnswS=5, content="22-39"),
                        PossibleAnswersS(idPosAnswS=5, content="40-69"),
                        PossibleAnswersS(idPosAnswS=5, content="70+"),
                        PossibleAnswersS(idPosAnswS=7, content="M"),
                        PossibleAnswersS(idPosAnswS=7, content="F"),
                        PossibleAnswersS(idPosAnswS=16, content="Si"),
                        PossibleAnswersS(idPosAnswS=16, content="No"),
                        PossibleAnswersS(idPosAnswS=18, content="1"),
                        PossibleAnswersS(idPosAnswS=18, content="2"),
                        PossibleAnswersS(idPosAnswS=18, content="3"),
                        PossibleAnswersS(idPosAnswS=18, content="4"),
                        PossibleAnswersS(idPosAnswS=18, content="5"),
                        PossibleAnswersS(idPosAnswS=23, content="Si"),
                        PossibleAnswersS(idPosAnswS=23, content="No"),
                        PossibleAnswersM(idPosAnswM=15, content="lunedì"),
                        PossibleAnswersM(idPosAnswM=15, content="martedì"),
                        PossibleAnswersM(idPosAnswM=15, content="mercoledì"),
                        PossibleAnswersM(idPosAnswM=15, content="giovedì"),
                        PossibleAnswersM(idPosAnswM=15, content="venerdì"),
                        PossibleAnswersM(idPosAnswM=15, content="sabato"),
                        PossibleAnswersM(idPosAnswM=15, content="domenica")])
    db_session.commit()


# function that add or edit a question in the db (with tags and possible answers)
def question_db(type, req, form_id, question_id):
    # Checking if the questions is mandatory
    mand = req.get("mandatory") == "on"

    # if import a questions
    if req.get("choose") == "yes":
        id_q = req.get("question_choose")  # Getting the id of the question the user want to import

        # link the question with the form (insert or update)
        if type == 'add':
            db_session.add(FormsQuestions(form_id=form_id, question_id=id_q, mandatory=mand))
        elif type == 'edit':
            db_session.query(FormsQuestions).filter(FormsQuestions.form_id == form_id).filter(
                FormsQuestions.question_id == question_id) \
                .update({FormsQuestions.question_id: id_q, FormsQuestions.mandatory: mand}, synchronize_session=False)
        db_session.commit()

    # if not import a questions
    else:
        tag_list = req.getlist("tag_choose")  # List of string with the id of chosen tags

        # create new Tag
        for tag in tag_list:
            # If in the tag list is also present the string "new"
            if tag == "new":

                new_tag = req.get("tag_added")  # Text of the Tag

                # Cheking if the ag already exists and adding the tag to the database
                if db_session.query(Tags).filter(Tags.argument == new_tag).first():
                    return "THIS TAG ALREADY EXISTS"

                aux = Tags(argument=new_tag)
                db_session.add(aux)
                db_session.commit()

                # Replace "new" with the tag id
                tag_list.remove("new")
                tag_list = tag_list + [str(aux.id)]

        tipo_domanda = req.get("question_type")  # Open, single or multiple_choice
        text_question = req.get("text_question")  # Text of the questions

        # Type of the question
        if tipo_domanda == "open":

            # Add the question
            q = Questions(text=text_question)
            db_session.add(q)
            db_session.commit()

            # In open questions we check has_file checkbox
            has_file = req.get('file_choose') == 'si'

            db_session.add(OpenQuestions(id=q.id))
            db_session.commit()

            # link the question with the tags
            for t in tag_list:
                db_session.add(TagsQuestions(tag_id=int(t), question_id=q.id))

            # link the question with the form (insert or update)
            if type == 'add':
                db_session.add(FormsQuestions(form_id=form_id, question_id=q.id, mandatory=mand, has_file=has_file))
            elif type == 'edit':
                db_session.query(FormsQuestions).filter(FormsQuestions.form_id == form_id).filter(
                    FormsQuestions.question_id == question_id) \
                    .update({FormsQuestions.question_id: q.id, FormsQuestions.mandatory: mand})

        elif tipo_domanda == "single":
            # add the new question
            q = Questions(text=text_question)
            db_session.add(q)
            db_session.commit()

            db_session.add(SingleQuestions(id=q.id))
            db_session.commit()

            # link the question with the tags
            for t in tag_list:
                db_session.add(TagsQuestions(tag_id=int(t), question_id=q.id))

            # add the possibile answers
            number = req.get("number_answers")  # form input text: how many possible answers?

            for i in range(1, int(number) + 1):
                cont = req.get(str(i))  # form input text: content of possible answers
                db_session.add(PossibleAnswersS(idPosAnswS=q.id, content=cont))

            # link the question with the form (insert or update)
            if type == 'add':
                db_session.add(FormsQuestions(form_id=form_id, question_id=q.id, mandatory=mand))
            elif type == 'edit':
                db_session.query(FormsQuestions).filter(FormsQuestions.form_id == form_id).filter(
                    FormsQuestions.question_id == question_id) \
                    .update({FormsQuestions.question_id: q.id, FormsQuestions.mandatory: mand})

        elif tipo_domanda == "multiple_choice":
            # add the new question
            q = Questions(text=text_question)
            db_session.add(q)
            db_session.commit()
            db_session.add(MultipleChoiceQuestions(id=q.id))
            db_session.commit()

            # link the question with the tags
            for t in tag_list:
                db_session.add(TagsQuestions(tag_id=int(t), question_id=q.id))

            # add the possibile answers
            number = req.get("number_answers")  # form input text: how many possible answers?

            for i in range(1, int(number) + 1):
                cont = req.get(str(i))  # form input text: content of possible answers
                db_session.add(PossibleAnswersM(idPosAnswM=q.id, content=cont))

            # link the question with the form (insert or update)
            if type == 'add':
                db_session.add(FormsQuestions(form_id=form_id, question_id=q.id, mandatory=mand))
            elif type == 'edit':
                db_session.query(FormsQuestions).filter(FormsQuestions.form_id == form_id).filter(
                    FormsQuestions.question_id == question_id) \
                    .update({FormsQuestions.question_id: q.id, FormsQuestions.mandatory: mand})

        db_session.commit()


# Deleting the form (all the other tables take advantages from CASCADE property)
def delete_form(f_id):
    db_session.query(Forms).filter(Forms.id == f_id).delete()
    db_session.commit()


# Materialized views creation
def create_mat_view():
    conn = engine.connect()
    conn.execute(
        "CREATE MATERIALIZED VIEW f_questions AS SELECT questions.* FROM questions, forms_questions, " +
        "forms WHERE forms_questions.question_id = questions.id AND forms_questions.form_id = forms.id")
    conn.execute(
        "CREATE MATERIALIZED VIEW f_answers AS SELECT answers.* FROM answers, forms " +
        "WHERE answers.form_id = forms.id")
    conn.close()


# TEMPLATE FUNCTION
def template_party(id_user, name, description):
    f = Forms(name=name, dataCreation=datetime.now(),
              description=description,
              creator_id=id_user)
    db_session.add(f)
    db_session.commit()

    db_session.add_all([FormsQuestions(form_id=f.id, question_id=1),
                        FormsQuestions(form_id=f.id, question_id=2),
                        FormsQuestions(form_id=f.id, question_id=11),
                        FormsQuestions(form_id=f.id, question_id=15),
                        FormsQuestions(form_id=f.id, question_id=13),
                        FormsQuestions(form_id=f.id, question_id=16)])
    db_session.commit()


def template_meets(id_user, name, description):
    f = Forms(name=name, dataCreation=datetime.now(),
              description=description,
              creator_id=id_user)
    db_session.add(f)
    db_session.commit()

    db_session.add_all([FormsQuestions(form_id=f.id, question_id=1),
                        FormsQuestions(form_id=f.id, question_id=2),
                        FormsQuestions(form_id=f.id, question_id=4),
                        FormsQuestions(form_id=f.id, question_id=7),
                        FormsQuestions(form_id=f.id, question_id=8),
                        FormsQuestions(form_id=f.id, question_id=13),
                        FormsQuestions(form_id=f.id, question_id=20, mandatory=True),
                        FormsQuestions(form_id=f.id, question_id=27, has_file=True)])
    db_session.commit()


def template_events(id_user, name, description):
    f = Forms(name=name, dataCreation=datetime.now(),
              description=description,
              creator_id=id_user)
    db_session.add(f)
    db_session.commit()

    db_session.add_all([FormsQuestions(form_id=f.id, question_id=1),
                        FormsQuestions(form_id=f.id, question_id=2),
                        FormsQuestions(form_id=f.id, question_id=3),
                        FormsQuestions(form_id=f.id, question_id=5),
                        FormsQuestions(form_id=f.id, question_id=16),
                        FormsQuestions(form_id=f.id, question_id=20)])
    db_session.commit()


def template_contacts(id_user, name, description):
    f = Forms(name=name, dataCreation=datetime.now(),
              description=description,
              creator_id=id_user)
    db_session.add(f)
    db_session.commit()

    db_session.add_all([FormsQuestions(form_id=f.id, question_id=1),
                        FormsQuestions(form_id=f.id, question_id=2),
                        FormsQuestions(form_id=f.id, question_id=5),
                        FormsQuestions(form_id=f.id, question_id=6),
                        FormsQuestions(form_id=f.id, question_id=7),
                        FormsQuestions(form_id=f.id, question_id=8),
                        FormsQuestions(form_id=f.id, question_id=9),
                        FormsQuestions(form_id=f.id, question_id=10)])
    db_session.commit()


# Base answers
def init_base_answers():
    # Andrea Marin: standard user
    user_id = 2

    # Template Party user: Andrea
    form_id = 1
    db_session.add_all([Answers(form_id=form_id, question_id=1, user_id=user_id),
                        Answers(form_id=form_id, question_id=2, user_id=user_id),
                        Answers(form_id=form_id, question_id=11, user_id=user_id),
                        Answers(form_id=form_id, question_id=13, user_id=user_id),
                        Answers(form_id=form_id, question_id=15, user_id=user_id),
                        Answers(form_id=form_id, question_id=16, user_id=user_id)])
    db_session.commit()

    db_session.add_all([SeqAnswers(id=1, content='Andrea'),
                        SeqAnswers(id=2, content='Marin'),
                        SeqAnswers(id=3, content='22:30'),
                        SeqAnswers(id=4, content='4'),
                        SeqAnswers(id=5, content='sabato'),
                        SeqAnswers(id=5, content='domenica'),
                        SeqAnswers(id=6, content='Si')
                        ])
    db_session.commit()

    # Template Meets
    form_id = 2
    db_session.add_all([Answers(form_id=form_id, question_id=1, user_id=user_id),
                        Answers(form_id=form_id, question_id=2, user_id=user_id),
                        Answers(form_id=form_id, question_id=4, user_id=user_id),
                        Answers(form_id=form_id, question_id=7, user_id=user_id),
                        Answers(form_id=form_id, question_id=8, user_id=user_id),
                        Answers(form_id=form_id, question_id=13, user_id=user_id),
                        Answers(form_id=form_id, question_id=20, user_id=user_id),
                        Answers(form_id=form_id, question_id=27, user_id=user_id)
                        ])
    db_session.commit()

    db_session.add_all([SeqAnswers(id=7, content='Andrea'),
                        SeqAnswers(id=8, content='Marin'),
                        SeqAnswers(id=9, content='23'),
                        SeqAnswers(id=10, content='M'),
                        SeqAnswers(id=11, content='andrea_marin@db.com'),
                        SeqAnswers(id=12, content='12'),
                        SeqAnswers(id=13, content='No'),
                        SeqAnswers(id=14, content='Nessun file')
                        ])
    db_session.commit()

    # Template Events
    form_id = 3
    db_session.add_all([Answers(form_id=form_id, question_id=1, user_id=user_id),
                        Answers(form_id=form_id, question_id=2, user_id=user_id),
                        Answers(form_id=form_id, question_id=3, user_id=user_id),
                        Answers(form_id=form_id, question_id=5, user_id=user_id),
                        Answers(form_id=form_id, question_id=16, user_id=user_id),
                        Answers(form_id=form_id, question_id=20, user_id=user_id)
                        ])
    db_session.commit()

    db_session.add_all([SeqAnswers(id=15, content='Andrea'),
                        SeqAnswers(id=16, content='Marin'),
                        SeqAnswers(id=17, content='29/02/1992'),
                        SeqAnswers(id=18, content='22-39'),
                        SeqAnswers(id=19, content='Si'),
                        SeqAnswers(id=20, content='Nessuna')
                        ])
    db_session.commit()

    # Template Contacts
    form_id = 4
    db_session.add_all([Answers(form_id=form_id, question_id=1, user_id=user_id),
                        Answers(form_id=form_id, question_id=2, user_id=user_id),
                        Answers(form_id=form_id, question_id=5, user_id=user_id),
                        Answers(form_id=form_id, question_id=6, user_id=user_id),
                        Answers(form_id=form_id, question_id=7, user_id=user_id),
                        Answers(form_id=form_id, question_id=8, user_id=user_id),
                        Answers(form_id=form_id, question_id=9, user_id=user_id),
                        Answers(form_id=form_id, question_id=10, user_id=user_id)
                        ])
    db_session.commit()

    db_session.add_all([SeqAnswers(id=21, content='Andrea'),
                        SeqAnswers(id=22, content='Marin'),
                        SeqAnswers(id=23, content='70+'),
                        SeqAnswers(id=24, content='Professore e ricercatore'),
                        SeqAnswers(id=25, content='M'),
                        SeqAnswers(id=26, content='andrea_marin@db.com'),
                        SeqAnswers(id=27, content='Venezia Mestre'),
                        SeqAnswers(id=28, content='Via Roma, 143')
                        ])
    db_session.commit()

    # Template Party user: Pippo
    user_id = 3
    form_id = 1
    db_session.add_all([Answers(form_id=form_id, question_id=1, user_id=user_id),
                        Answers(form_id=form_id, question_id=2, user_id=user_id),
                        Answers(form_id=form_id, question_id=11, user_id=user_id),
                        Answers(form_id=form_id, question_id=13, user_id=user_id),
                        Answers(form_id=form_id, question_id=15, user_id=user_id),
                        Answers(form_id=form_id, question_id=16, user_id=user_id)])
    db_session.commit()

    db_session.add_all([SeqAnswers(id=29, content='Pippo'),
                        SeqAnswers(id=30, content='Franchetti'),
                        SeqAnswers(id=31, content='00:30'),
                        SeqAnswers(id=32, content='43'),
                        SeqAnswers(id=33, content='venerdì'),
                        SeqAnswers(id=33, content='sabato'),
                        SeqAnswers(id=33, content='lunedì'),
                        SeqAnswers(id=34, content='Si')
                        ])
    db_session.commit()
