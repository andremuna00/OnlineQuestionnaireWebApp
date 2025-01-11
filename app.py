import os
import secrets

from flask import Flask, redirect, url_for, send_from_directory, request
from flask_mail import Mail
from flask_security import Security, auth_required, logout_user, \
    SQLAlchemySessionUserDatastore
from flask_security.forms import ConfirmRegisterForm, Required
from flask_security.utils import hash_password
from flask_babelex import Babel
from wtforms import TextField, DateField
from dotenv import load_dotenv

from form_function import *
from users_info_BP import users_info_BP
from form_edit_BP import form_edit_BP
from form_add_BP import form_add_BP
from form_view_BP import form_view_BP

from models import *
from datetime import date, datetime

# SETUP FLASK
# Create app, setup Babel communication and Mail configuration, BluePrint Registration
app = Flask(__name__)
app.register_blueprint(form_edit_BP)
app.register_blueprint(form_add_BP)
app.register_blueprint(form_view_BP)
app.register_blueprint(users_info_BP)
init_db()

# LIST OF CONFIGS
app.config['DEBUG'] = True
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'Info.progbd.dblegends@gmail.com'
app.config['MAIL_PASSWORD'] = 'db_legends00'
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_EMAIL_SUBJECT_REGISTER'] = 'Welcome to DB_Legends\'s app'
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_POST_CONFIRM_VIEW'] = '/add_role_post'
app.config['SECURITY_CONFIRM_EMAIL_WITHIN'] = '1 days'
app.config['SECURITY_POST_LOGIN_VIEW'] = '/'
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_RESET_PASSWORD_WITHIN'] = '1 days'

# Generate a nice key using secrets.token_urlsafe() inside a .env file
if not os.path.isfile('.env'):
    confFile = open('.env', 'w')
    confFile.write('SECRET_KEY=' + str(secrets.token_urlsafe()) + '\n')
    confFile.write('SECURITY_PASSWORD_SALT=' + str(secrets.SystemRandom().getrandbits(128)))
    confFile.close()

load_dotenv()

# Reading vars from file .env created before
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SECURITY_PASSWORD_SALT'] = os.environ['SECURITY_PASSWORD_SALT']


# extends RegisterForm of flask
class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
    name = TextField('Nome', [Required()])
    surname = TextField('Cognome', [Required()])
    date = DateField('Data di nascita', format='%d-%m-%Y', default=date.today())
    username = TextField('Username', [Required()])


# Linking flask-security with user and role table
user_datastore = SQLAlchemySessionUserDatastore(db_session, Users, Roles)

# Init mail, babel e security
security = Security(app, user_datastore, confirm_register_form=ExtendedConfirmRegisterForm)
mail = Mail(app)
babel = Babel(app)

# Monkeypatching Flask-babelex (necessary to setup flask-security)
babel.domain = 'flask_user'
babel.translation_directories = 'translations'


# Database population
@app.before_first_request
def init():
    if not user_datastore.find_user(email="admin@db.com"):
        create_mat_view()
        create_roles()
        create_superuser()
        create_standard_users()
        populate_tags()
        init_base_question()
        template_party(1, "Party Form", "Invito per una festa")
        template_meets(1, "Meets Form", "Meeting")
        template_events(1, "Events Form", "Evento")
        template_contacts(1, "Form Informativo", "Informazioni personali")
        init_base_answers()


# Create all the roles
def create_roles():
    user_datastore.create_role(name="Admin", description="App administrator")
    user_datastore.create_role(name="SuperUser", description="User with all privileges")
    user_datastore.create_role(name="Standard User", description="Standard app user")
    db_session.commit()


# Create the first user with all the roles
def create_superuser():
    user_datastore.create_user(email="admin@db.com", password=hash_password("password"),
                               username="admin", name="Admin", surname="Admin", date=date.today(),
                               confirmed_at=datetime.now())
    db_session.commit()

    admin = db_session.query(Users).filter(Users.id == 1).first()

    role = user_datastore.find_role("Admin")
    user_datastore.add_role_to_user(admin, role)

    role = user_datastore.find_role("SuperUser")
    user_datastore.add_role_to_user(admin, role)

    role = user_datastore.find_role("Standard User")
    user_datastore.add_role_to_user(admin, role)

    db_session.commit()


# Create the other 2 standard users
def create_standard_users():
    user_datastore.create_user(email="andrea_marin@db.com", password=hash_password("password"),
                               username="andreamarin35", name="Andrea", surname="Marin", date=date.today(),
                               confirmed_at=datetime.now())

    user_datastore.create_user(email="topolino@db.com", password=hash_password("password"),
                               username="topolino123", name="Pippo", surname="Franchetti", date=date.today(),
                               confirmed_at=datetime.now())

    db_session.commit()
    sd_user = db_session.query(Users).filter(Users.id == 2).first()
    role = user_datastore.find_role("Standard User")
    user_datastore.add_role_to_user(sd_user, role)

    sd_user = db_session.query(Users).filter(Users.id == 3).first()
    role = user_datastore.find_role("Standard User")
    user_datastore.add_role_to_user(sd_user, role)
    db_session.commit()


# HomePage
@app.route("/")
def home():
    return render_template("index.html", user=current_user)


# Favicon of the webpages
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Logout
@app.route("/logout")
@auth_required()
def logout():
    logout_user()
    return redirect(url_for('home'))


# GET: visualize the user profile
# POST: delete the user
@app.route("/profile", methods=['GET', 'POST'])
@auth_required()
def user_profile():
    superuser_role = db_session.query(Roles).filter(Roles.name == "SuperUser").first()
    admin_role = db_session.query(Roles).filter(Roles.name == "Admin").first()
    is_superuser = True if (superuser_role in current_user.roles) else False
    is_admin = True if (admin_role in current_user.roles) else False

    if request.method == 'POST':
        # The superuser can not be deleted
        if not is_superuser:
            id_user = current_user.id
            logout_user()

            db_session.query(Users).filter(Users.id == id_user).delete()
            db_session.commit()
            return redirect(url_for("home"))

    return render_template("profile.html", user=current_user, is_superuser=is_superuser, is_admin=is_admin)


# GET: render the page to edit the profile
# POST: send the request with the edit fields
@app.route("/profile/edit", methods=['GET', 'POST'])
@auth_required()
def edit_profile():
    if request.method == 'POST':
        req = request.form
        db_session.query(Users).filter(Users.id == current_user.id).update({"name": req.get("name"),
                                                                            "surname": req.get("surname"),
                                                                            "date": req.get("b_date"),
                                                                            "username": req.get("username")
                                                                            })
        db_session.commit()
        return redirect(url_for('user_profile'))

    return render_template("edit_profile.html", user=current_user)


# Endpoint necessary to add a role to a new user
@app.route("/add_role_post")
@auth_required()
def add_role():
    if not current_user.roles:
        role = user_datastore.find_role("Standard User")
        user_datastore.add_role_to_user(current_user, role)
        db_session.commit()
    return redirect(url_for("home"))


# Run the app
if __name__ == '__main__':
    app.run()
