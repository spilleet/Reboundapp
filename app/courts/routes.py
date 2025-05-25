import os
from flask import render_template, flash, redirect, url_for, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.courts import bp
from app.courts.forms import CourtForm
from app.models import Court, Game, GameParticipant
from app import db

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/courts')
def list_courts():
    courts = Court.query.all()
    return render_template('courts/list.html', title='경기장 목록', courts=courts)

@bp.route('/courts/new', methods=['GET', 'POST'])
@login_required
def create_court():
    form = CourtForm()
    if form.validate_on_submit():
        court = Court(
            name=form.name.data,
            location=form.location.data,
            opening_time=form.opening_time.data,
            closing_time=form.closing_time.data,
            wheelchair_rental=form.wheelchair_rental.data,
            wheelchair_ramp=form.wheelchair_ramp.data,
            elevator=form.elevator.data,
            adjustable_basket=form.adjustable_basket.data,
            created_by=current_user.id
        )
        
        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            filename = f"court_{court.id}_{filename}"
            file.save(os.path.join('app/static/uploads', filename))
            court.image_path = filename
        
        db.session.add(court)
        db.session.commit()
        
        flash('경기장이 성공적으로 등록되었습니다.')
        return redirect(url_for('courts.court_detail', id=court.id))
    return render_template('courts/create.html', title='경기장 등록', form=form)

@bp.route('/courts/<int:id>')
def court_detail(id):
    court = Court.query.get_or_404(id)
    return render_template('courts/detail.html', title='경기장 상세 정보', court=court)

@bp.route('/courts/<int:id>/delete', methods=['POST'])
@login_required
def delete_court(id):
    court = Court.query.get_or_404(id)
    if court.created_by != current_user.id:
        abort(403)  # Forbidden
    
    # 해당 경기장의 모든 경기 찾기
    games = Game.query.filter_by(court_id=id).all()
    
    # 각 경기의 참가자 정보와 경기 삭제
    for game in games:
        GameParticipant.query.filter_by(game_id=game.id).delete()
        db.session.delete(game)
    
    # 이미지 파일 삭제
    if court.image_path:
        try:
            os.remove(os.path.join('app/static/uploads', court.image_path))
        except:
            pass  # 파일이 없거나 삭제 실패해도 계속 진행
    
    # 경기장 삭제
    db.session.delete(court)
    db.session.commit()
    flash('경기장이 삭제되었습니다.')
    return redirect(url_for('courts.list_courts')) 