from flask import Blueprint, redirect, url_for
from flask_security import auth_required
from form_function import *

# Users management endpoints for Admin or SuperUser roles
users_info_BP = Blueprint('users_info_BP', __name__, url_prefix='/users_info')


# Admin + SuperUser --> can see all the users and their forms
@users_info_BP.route("/")
@auth_required()
@admin_role_required
def sudo_view_users_info():
    superusers = db_session.query(Users.id).join(RolesUsers, Users.id == RolesUsers.user_id). \
        join(Roles, Roles.id == RolesUsers.role_id).filter(Roles.name == "SuperUser")
    admins = db_session.query(Users.id).join(RolesUsers, Users.id == RolesUsers.user_id). \
        join(Roles, Roles.id == RolesUsers.role_id).filter(Roles.name == "Admin")

    users = db_session.query(Users).filter(Users.id.not_in(superusers)).all()
    std_users = db_session.query(Users).filter(Users.id.not_in(superusers)).filter(Users.id.not_in(admins)).all()

    admin_role = db_session.query(Roles).filter(Roles.name == "Admin").first()
    superuser_role = db_session.query(Roles).filter(Roles.name == "SuperUser").first()
    return render_template("users_info.html", users=users, admin_role=admin_role, superuser_role=superuser_role, std_users=std_users)


# Admin --> can enable all the Standard User
# SuperUser --> can enable all the Admin and Standard User
@users_info_BP.route("/<user_id>/enable")
@auth_required()
@admin_role_required
def sudo_enable_enable(user_id):
    from app import user_datastore

    user = db_session.query(Users).filter(Users.id == user_id).first()
    if not user:
        return render_template("error.html", message="This user not exist")
    user_datastore.activate_user(user)
    db_session.commit()
    return redirect(url_for("users_info_BP.sudo_view_users_info"))


# Admin --> can disable all the Standard User
# SuperUser --> can disable all the Admin and Standard User
@users_info_BP.route("/<user_id>/disable")
@auth_required()
@admin_role_required
def sudo_enable_disable(user_id):

    user = db_session.query(Users).filter(Users.id == user_id).first()
    if not user:
        return render_template("error.html", message="This user not exist")

    from app import user_datastore
    user_datastore.deactivate_user(user)
    db_session.commit()
    return redirect(url_for("users_info_BP.sudo_view_users_info"))


# Admin --> can delete all the Standard User
# SuperUser --> can delete all the Admin and Standard User
@users_info_BP.route("/<user_id>/delete")
@auth_required()
@admin_role_required
def sudo_delete_user(user_id):
    user_query = db_session.query(Users).filter(Users.id == user_id)
    user = user_query.first()
    if not user:
        return render_template("error.html", message="This user not exist")

    user_query.delete()
    db_session.commit()
    return redirect(url_for("users_info_BP.sudo_view_users_info"))


# Admin --> can delete all the Standard User's form
# SuperUser --> can delete all the Admin and Standard User's form
@users_info_BP.route("/form/<form_id>/delete")
@auth_required()
@admin_role_required
def sudo_delete_form(form_id):
    form = db_session.query(Forms).filter(Forms.id == form_id).first()
    if not form:
        return render_template("error.html", message="This form not exist")
    delete_form(form_id)
    return redirect(url_for("users_info_BP.sudo_view_users_info"))


# SuperUser --> can grant Admin privileges to a Standard User
@users_info_BP.route("/<user_id>/grant")
@auth_required()
@superuser_role_required
def sudo_grant_user(user_id):
    user = db_session.query(Users).filter(Users.id == user_id).first()
    role = db_session.query(Roles).filter(Roles.name == "Admin").first()
    if not user:
        return render_template("error.html", message="This user not exist")

    from app import user_datastore
    user_datastore.add_role_to_user(user, role)
    db_session.commit()
    return redirect(url_for("users_info_BP.sudo_view_users_info"))


# SuperUser --> can revoke Admin privileges to a Standard User
@users_info_BP.route("/<user_id>/revoke")
@auth_required()
@superuser_role_required
def sudo_revoke_user(user_id):
    user = db_session.query(Users).filter(Users.id == user_id).first()
    role = db_session.query(Roles).filter(Roles.name == "Admin").first()
    if not user:
        return render_template("error.html", message="This user not exist")

    from app import user_datastore
    user_datastore.remove_role_from_user(user, role)
    db_session.commit()
    return redirect(url_for("users_info_BP.sudo_view_users_info"))
