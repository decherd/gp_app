from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from .. import db, bcrypt
from ..models import User, UserType
from .forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm, UserTypeForm)
from .utils import send_reset_email

users = Blueprint('users', __name__)


# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for('auth.login'))

#         return view(**kwargs)

#     return wrapped_view

@users.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in.', 'success')
		return redirect(url_for('users.login'))
	return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('main.home'))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')
	return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('users.account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email

	return render_template('account.html', title='Account', form=form)

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset your password', 'info')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token.', 'warning')
		return redirect(url_for('users.reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated! You are now able to log in.', 'success')
		return redirect(url_for('users.login'))
	return render_template('reset_token.html', title='Reset Password', form=form)

@users.route("/user_types")
def user_types():
	user_types = UserType.query.all()
	return render_template('user_types.html', title='User Types', user_types=user_types)


@users.route("/user_type/new", methods=['GET', 'POST'])
@login_required
def new_user_type():
	form = UserTypeForm()
	if form.validate_on_submit():
		flash('A new user type has been added!', 'success')
		user_type = UserType(name=form.name.data)
		db.session.add(user_type)
		db.session.commit()
		return redirect(url_for('users.user_types'))
	return render_template('add_user_type.html', title='New User Type', legend="New User Type", form=form)


@users.route("/user_type/<int:user_type_id>/delete", methods=['POST'])
@login_required
def delete_user_type(user_type_id):
	user_type = UserType.query.get_or_404(user_type_id)
	db.session.delete(user_type)
	db.session.commit()
	flash('The user type has been deleted!', 'success')
	return redirect(url_for('users.user_types'))


@users.route("/user_type/<int:user_type_id>/update", methods=['GET', 'POST'])
@login_required
def update_user_type(user_type_id):
	user_type = UserType.query.get_or_404(user_type_id)
	form = UserTypeForm()
	if form.validate_on_submit():
		user_type.name = form.name.data
		db.session.commit()
		flash('Your user type has been updated!', 'success')
		return redirect(url_for('users.user_types'))
	elif request.method == "GET":
		form.name.data = user_type.name
	return render_template('add_user_type.html', title='Update User Type', form=form, 
							legend="Update User Type")