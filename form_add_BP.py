from flask import Blueprint, request, redirect, url_for
from flask_security import auth_required

from form_function import *

# Contains endpoints relative for adding new elements in the db
form_add_BP = Blueprint('form_add_BP', __name__, template_folder='templates/form', url_prefix='/form')


# GET: render template to create a new form
# POST: send a request to create or import a new form
@form_add_BP.route("/form_create", methods=['GET', 'POST'])
@auth_required()
def form_create():
    if request.method == "POST":
        req = request.form

        imp = req.get("import")  # if the user want to import an exisiting form

        nome = req.get("name")  # form's name

        # Checking that a form with the same name is not present
        exist_form = db_session.query(Forms).filter(Forms.name == nome).filter(
            Forms.creator_id == current_user.id).first()
        if exist_form:
            return render_template("error.html", message="You have already created a form with this name")

        descrizione = req.get("description")  # form's description

        # if import
        if imp == "yes":
            template = req.get("template")  # id of the template/form

            if template == '1':
                template_party(current_user.id, nome, descrizione)
            elif template == '2':
                template_events(current_user.id, nome, descrizione)
            elif template == '3':
                template_contacts(current_user.id, nome, descrizione)
            elif template == '4':
                template_meets(current_user.id, nome, descrizione)
            else:
                new_form = Forms(name=nome, dataCreation=datetime.now(),
                                 description=descrizione,
                                 creator_id=current_user.id)
                db_session.add(new_form)
                db_session.commit()

                curr_formsquestions = db_session.query(FormsQuestions).filter(FormsQuestions.form_id == int(template)).all()
                for q in curr_formsquestions:
                    db_session.add(FormsQuestions(form_id=new_form.id, question_id=q.question_id, mandatory=q.mandatory, has_file=q.has_file))

        # if not import
        else:
            db_session.add(Forms(name=nome, dataCreation=datetime.now(),
                                 description=descrizione,
                                 creator_id=current_user.id))

        db_session.commit()
        return redirect(url_for('form_view_BP.form'))

    # we pass the templates/forms that the user can import
    forms_template = db_session.query(Forms).filter((Forms.id == 1) | (Forms.id == 2) | (Forms.id == 3) |
                                                    (Forms.id == 4) | (Forms.creator_id == current_user.id))
    return render_template("form_create.html", user=current_user, forms=forms_template)


# GET: render the template with some dynamic html forms to create a question
# POST: insert a new question in the current form
@form_add_BP.route("/<form_id>/add_question", methods=['GET', 'POST'])
@auth_required()
@creator_or_admin_role_required
def form_add_question(form_id):

    current_form = db_session.query(Forms).filter(Forms.id == form_id).first()
    if not current_form:
        return render_template("error.html", message="This form not exist")

    # if a request for adding a question is sent
    if request.method == "POST":
        req = request.form

        # function that add/edit a question in the db
        # if an error is raised, the function will return the message error
        message = question_db("add", req, form_id, -1)

        if message:
            return render_template("error.html", message=message)
        else:
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

    return render_template("question_add_edit.html", form=current_form, tags=tags, questions=questions, edit=False)
