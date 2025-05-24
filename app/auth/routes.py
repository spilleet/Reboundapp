from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm, FindUsernameForm, FindPasswordForm, UpdateProfileForm
import secrets
import string

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('아이디나 비밀번호가 올바르지 않습니다.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', title='로그인', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('회원가입이 완료되었습니다!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='회원가입', form=form)

@bp.route('/find_username', methods=['GET', 'POST'])
def find_username():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = FindUsernameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash(f'회원님의 아이디는 {user.username} 입니다.')
            return redirect(url_for('auth.login'))
        flash('해당 이메일로 등록된 사용자가 없습니다.')
    return render_template('auth/find_username.html', title='아이디 찾기', form=form)

@bp.route('/find_password', methods=['GET', 'POST'])
def find_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = FindPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, email=form.email.data).first()
        if user:
            # 임시 비밀번호 생성 (16자리)
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
            user.set_password(temp_password)
            db.session.commit()
            flash(f'임시 비밀번호가 발급되었습니다: {temp_password}')
            return redirect(url_for('auth.login'))
        flash('입력하신 정보와 일치하는 사용자가 없습니다.')
    return render_template('auth/find_password.html', title='비밀번호 찾기', form=form)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm(current_user.username)
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            # 아이디 변경
            if form.username.data != current_user.username:
                current_user.username = form.username.data
            
            # 비밀번호 변경
            if form.new_password.data:
                current_user.set_password(form.new_password.data)
            
            db.session.commit()
            flash('프로필이 성공적으로 수정되었습니다.')
            return redirect(url_for('auth.profile'))
        else:
            flash('현재 비밀번호가 올바르지 않습니다.')
    return render_template('auth/profile.html', title='프로필 수정', form=form) 
