from flask import Blueprint, request, redirect, url_for, flash, make_response, Response
from flask_security import auth_required
from werkzeug.utils import secure_filename

from form_function import *

# Contains endpoints relative for viewing elements in the db
form_view_BP = Blueprint('form_view_BP', __name__, template_folder='templates/form', url_prefix='/form')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


# GET: Displays the list of the form with some buttons:
#       - Creating a new form
#       - Editing a form
#       - Copy the link of the form
#       - Deleting a form
# POST: request to delete a specific form
@form_view_BP.route("/", methods=['GET', 'POST'])
@auth_required()
def form():
    if request.method == 'POST':
        req = request.form

        f_id = req.get("form")  # Hidden form necessary to get the id
        delete_form(f_id)

        return redirect(url_for('form_view_BP.form'))

    forms_list = db_session.query(Forms).filter(Forms.creator_id == current_user.id)
    return render_template("forms_list.html", user=current_user, forms=forms_list)


# GET: what users see when they compile a form
# POST: send the form answers for the memorization
@form_view_BP.route("/<form_id>/viewform", methods=['GET', 'POST'])
@auth_required()
def form_view(form_id):
    current_form = db_session.query(Forms).filter(Forms.id == form_id).first()
    if not current_form:
        return render_template("error.html", message="This form does not exist")

    # check if the user already answered the form
    exist_answers = db_session.query(Answers).filter(Answers.form_id == form_id).filter(
        Answers.user_id == current_user.id).first()
    if exist_answers:
        return render_template("error.html", message="You have already filled out this form")

    if request.method == "POST":
        # Check if the uploaded files have the requirements before store them and store questions
        open_question_file_check = db_session.query(FormsQuestions)\
            .filter(FormsQuestions.form_id == form_id).filter(FormsQuestions.has_file).all()

        for tmp_id in open_question_file_check:
            file = request.files['file_' + str(tmp_id.question_id)]
            if file:
                filename = secure_filename(file.filename)
                if file.filename == '':
                    flash('No selected file in some questions', 'file_error')
                    return redirect(request.url)
                mimetype = file.mimetype
                if not filename or not mimetype:
                    flash('Bad uploads!', 'file_error')
                    return redirect(request.url)
                if not allowed_file(file.filename):
                    flash('Some file are not allowed', 'file_error')
                    return redirect(request.url)

        req = request.form

        # Get for every answered question
        for q in current_form.questions:
            if not q.multiple_choice:
                text = [req.get(str(q.id))]
            else:
                text = req.getlist(str(q.id))  # if is a multiple choice question we get multiple answers

            # We add the object: answers
            ans = Answers(form_id=form_id, question_id=q.id, user_id=current_user.id)
            db_session.add(ans)
            db_session.commit()

            # Check if the question is open question and if it allows file adding
            for tmp in q.open:
                query_has_file = db_session.query(FormsQuestions).filter(FormsQuestions.question_id == tmp.id).\
                    filter(FormsQuestions.has_file).first()
                if query_has_file:
                    # File memorization (the name and the extension was checked before)
                    file = None
                    if ('file_' + str(tmp.id)) in request.files:
                        file = request.files['file_' + str(tmp.id)]
                    if file:
                        filename = secure_filename(file.filename)
                        mimetype = file.mimetype
                        virtual_file = Files(data=file.read(), name=filename, mimetype=mimetype, answer_id=ans.id)
                        db_session.add(virtual_file)
                        db_session.commit()

            # we add all the answers (if the users leave a blank multiple choice/single answer we don't memorize
            # anything--> we prevent error in the javascript graphs)
            for t in text:
                if t:
                    db_session.add(SeqAnswers(id=ans.id, content=t))
                elif ans.question.open:
                    db_session.add(SeqAnswers(id=ans.id, content='blank'))

            db_session.commit()

        return redirect(url_for('home'))

    # The creator of a form can only edit the form and not answer it
    questions = db_session.query(Questions, FormsQuestions).filter(FormsQuestions.form_id == form_id).filter(
        Questions.id == FormsQuestions.question_id)
    if current_user.id != current_form.creator_id:
        return render_template("form_view.html", user=current_user, questions=questions, form=current_form)
    else:
        return render_template("form_edit.html", user=current_user, questions=questions, form=current_form)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Display the answers for a specific form
@form_view_BP.route("/<form_id>/answers")
@auth_required()
@creator_or_admin_role_required
def form_answers(form_id):
    current_form = db_session.query(Forms).filter(Forms.id == form_id).first()
    if not current_form:
        return render_template("error.html", message="This form does not exist")

    # List of all the answers of this form
    answers = db_session.query(Answers, Files).join(Files, Answers.id == Files.answer_id, isouter=True).filter(
        Answers.form_id == form_id)

    # Number of all the answers
    total_answers = db_session.query(Answers.user_id).filter(Answers.form_id == form_id).group_by(
        Answers.user_id).count()

    return render_template("form_answers.html", user=current_user, answers=answers, form=current_form,
                           total_answers=total_answers)


# Display files for a specific answer
@form_view_BP.route("/answers/<answer_id>")
@auth_required()
@creator_or_admin_role_required
def view_files(answer_id):
    # Getting the file
    file = db_session.query(Files).filter(Files.answer_id == answer_id).first()
    if not file:
        return render_template("error.html", message="This file does not exist")

    # creating an http-response message with the file
    response = make_response(file.data)
    response.headers['Content-Type'] = file.mimetype
    response.headers['Content-Disposition'] = 'inline; filename=%s' % file.name
    return response


# Route that allows to download a CSV file with all the answers of the form
@form_view_BP.route("/<form_id>/download_csv")
@auth_required()
@creator_or_admin_role_required
def download_csv_answers(form_id):
    current_form = db_session.query(Forms).filter(Forms.id == form_id).first()
    if not current_form:
        return render_template("error.html", message="This form does not exist")

    # Format of the csv lines
    answers_all = db_session.query(Users.username, Questions.text, SeqAnswers.content).filter(
        Answers.form_id == form_id).filter(
        Answers.id == SeqAnswers.id).filter(Users.id == Answers.user_id).filter(Questions.id == Answers.question_id)

    # Creating the csv file
    csv = ''
    for a in answers_all:
        csv = csv + a.username + ',' + a.text + ',' + a.content + '\n'

    # sending the csv file via http-response
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=answers.csv"})
