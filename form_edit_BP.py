
from flask import request, redirect, url_for, Blueprint
from flask_security import auth_required
from form_function import *

# Contains endpoints relative for editing existing elements in the db
form_edit_BP = Blueprint('form_edit_BP', __name__, template_folder='templates/form', url_prefix='/form')


# GET: render a form preview with the possibility of edit several things
# POST: request for removing a question from the form
@form_edit_BP.route("/<form_id>/edit", methods=['GET', 'POST'])
@auth_required()
@creator_or_admin_role_required
def form_edit(form_id):
    current_form = db_session.query(Forms).filter(Forms.id == form_id).first()
    if not current_form:
        return render_template("error.html", message="This form does not exist")

    if request.method == "POST":
        req = request.form

        id_q = req.get("question")  # Hidden form that grants the id of the question

        # We need to unlink the question from the form
        db_session.query(FormsQuestions).filter(FormsQuestions.form_id == form_id). \
            filter(FormsQuestions.question_id == id_q).delete()
        db_session.commit()

        # reload the page
        return redirect(url_for('form_edit_BP.form_edit', form_id=form_id))

    # questions + mandatory
    questions = db_session.query(Questions, FormsQuestions).filter(FormsQuestions.form_id == form_id). \
        filter(Questions.id == FormsQuestions.question_id)

    return render_template("form_edit.html", user=current_user, questions=questions, form=current_form)


# Only POST: request sent from the page "edit form"
# Allows to modify if a specific question is mandatory/has_file
@form_edit_BP.route("/<form_id>/<question_id>/flag", methods=['POST'])
@auth_required()
@creator_or_admin_role_required
def edit_mand_or_files(form_id, question_id):
    check_parameters = db_session.query(FormsQuestions).filter(FormsQuestions.form_id == form_id).\
        filter(FormsQuestions.question_id == question_id).first()
    if not check_parameters:
        return render_template("error.html", message="This form or this question does not exist")

    req = request.form

    # Hidden form useful to understand what type of request is sent
    if 'allows_file_hidden' in req:
        file = False
        # Checking value of checkbox
        if 'checkBox_file' in req:
            file = True

        db_session.query(FormsQuestions).filter(FormsQuestions.form_id == form_id). \
            filter(FormsQuestions.question_id == question_id).update({"has_file": file})
        db_session.commit()

    # Hidden form useful to understand what type of request is sent
    if 'mand_hidden' in req:
        mand = False
        # Checking value of checkbox
        if 'checkBox_mandatory' in req:
            mand = True

        db_session.query(FormsQuestions).filter(FormsQuestions.form_id == form_id). \
            filter(FormsQuestions.question_id == question_id).update({"mandatory": mand})
        db_session.commit()

    return redirect(url_for("form_edit_BP.form_edit", form_id=form_id))


# GET: render the page for editing the form main info (name and description)
# POST: store the edited current form name/description
@form_edit_BP.route("/<form_id>/editMainInfo", methods=['GET', 'POST'])
@auth_required()
@creator_or_admin_role_required
def form_edit_main_info(form_id):
    current_form = db_session.query(Forms).filter(Forms.id == form_id)
    if not current_form:
        return render_template("error.html", message="This form does not exist")

    if request.method == 'POST':
        req = request.form

        # Checking that the user does not use other forms' name
        exist_form = db_session.query(Forms).filter(Forms.name == req.get("name")).filter(
            Forms.creator_id == current_user.id).filter(Forms.id != form_id).first()
        if exist_form:
            return render_template("error.html", message="You have already created a form with this name")

        # Update
        current_form.update({"name": req.get("name"), "description": req.get("description")})
        db_session.commit()

        # goes to /<form_id>/edit
        return redirect(url_for('form_edit_BP.form_edit', form_id=form_id))

    return render_template("form_edit_main_info.html", form=current_form.first())


# GET: render the template with some dynamic html forms to create a question (smilar to add questions)
# POST: Request for editing a specific question (the entire question/only the possible answers)
@form_edit_BP.route("/<form_id>/<question_id>", methods=['GET', 'POST'])
@auth_required()
@creator_or_admin_role_required
def form_edit_question(form_id, question_id):
    current_form = db_session.query(Forms).filter(Forms.id == form_id).first()
    current_question = db_session.query(Questions).filter(Questions.id == question_id).first()

    if (not current_form) or (not current_question):
        return render_template("error.html", message="This form or this question does not exist")

    check_parameters = db_session.query(FormsQuestions).filter(FormsQuestions.form_id == form_id). \
        filter(FormsQuestions.question_id == question_id).first()
    if not check_parameters:
        return render_template("error.html", message="This question is not present in the current form")

    if request.method == "POST":
        req = request.form

        c = req.get("change")  # Check if the user want to change question or possible answers
        mand = req.get("mandatory") == "on"

        # if the user want to change the possible answers
        if c == 'possible_a':
            if current_question.multiple_choice:
                # add the new question (same to the previous one)
                q = Questions(text=current_question.text)
                db_session.add(q)
                db_session.commit()

                db_session.add(MultipleChoiceQuestions(id=q.id))
                db_session.commit()

                tags = db_session.query(TagsQuestions).filter(TagsQuestions.question_id == question_id).all()
                # link the question with the tag (same to the previous one)
                for t in tags:
                    db_session.add(TagsQuestions(tag_id=t.tag_id, question_id=q.id))

                # add the new possibile answers
                number = req.get("number_answers")  # form input text: how many possible answers?

                for i in range(1, int(number) + 1):
                    cont = req.get(str(i))  # form input text: content of possible answers
                    db_session.add(PossibleAnswersM(idPosAnswM=q.id, content=cont))

                # Update the question in the form
                db_session.query(FormsQuestions).filter(FormsQuestions.form_id == form_id). \
                    filter(FormsQuestions.question_id == question_id).update({"question_id": q.id, "mandatory": mand})

            elif current_question.single:

                # add the new question (same to the previous one)
                q = Questions(text=current_question.text)
                db_session.add(q)
                db_session.commit()

                db_session.add(SingleQuestions(id=q.id))
                db_session.commit()

                tags = db_session.query(TagsQuestions).filter(TagsQuestions.question_id == question_id).all()
                # link the question with the tag (same to the previous one)
                for t in tags:
                    db_session.add(TagsQuestions(tag_id=t.tag_id, question_id=q.id))

                # add the new possibile answers
                number = req.get("number_answers")  # form input text: how many possible answers?

                for i in range(1, int(number) + 1):
                    cont = req.get(str(i))  # form input text: content of possible answers
                    db_session.add(PossibleAnswersS(idPosAnswS=q.id, content=cont))

                # Update the question in the form
                db_session.query(FormsQuestions).filter(FormsQuestions.form_id == form_id). \
                    filter(FormsQuestions.question_id == question_id).update({"question_id": q.id, "mandatory": mand})

            db_session.commit()

        # if the user want to change the question we use the function question_db
        else:
            # function that add/edit a question in the db
            # if an error raises, the function will return the message error
            message = question_db("edit", req, form_id, question_id)

            if message:
                return render_template("error.html", message=message)

        # goes to /<form_id>/edit
        return redirect(url_for('form_edit_BP.form_edit', form_id=form_id))

    # For importing the existing question is necessary to pass some data to the template
    # List of the tags
    tags = db_session.query(Tags)

    # Questions created by the users
    q = db_session.query(Questions).filter(Questions.id == FormsQuestions.question_id). \
        filter(Forms.creator_id == current_user.id).filter(FormsQuestions.form_id == Forms.id)

    # Questions created by admins
    q2 = db_session.query(Questions).filter(Questions.id == FormsQuestions.question_id). \
        filter(Forms.creator_id == Users.id).filter(FormsQuestions.form_id == Forms.id).filter(Roles.name == "Admin"). \
        filter(Roles.id == RolesUsers.role_id).filter(Users.id == RolesUsers.user_id)

    # Base Questions
    q3 = db_session.query(Questions).filter(Questions.id > 0).filter(Questions.id < 28)

    # List of importable questions
    questions = (q.union(q2)).union(q3)

    # We pass the number of possible answers that the current question has
    number = 0
    if current_question.single:
        number = db_session.query(PossibleAnswersS).filter(PossibleAnswersS.idPosAnswS == question_id).count()
    elif current_question.multiple_choice:
        number = db_session.query(PossibleAnswersM).filter(PossibleAnswersM.idPosAnswM == question_id).count()

    mand = db_session.query(FormsQuestions.mandatory).filter(FormsQuestions.form_id == form_id).filter(
        question_id == FormsQuestions.question_id).first()[0]


    return render_template("question_add_edit.html", form=current_form, tags=tags, questions=questions, q=current_question,
                           edit=True, number=number, mand=mand)



