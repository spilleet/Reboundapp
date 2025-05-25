from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user
from app.games import bp
from app.games.forms import GameForm
from app.models import Game, Court, GameParticipant
from app import db

@bp.route('/games/new', methods=['GET', 'POST'])
@login_required
def create_game():
    form = GameForm()
    form.court_id.choices = [(c.id, c.name) for c in Court.query.all()]
    
    if form.validate_on_submit():
        game = Game(
            court_id=form.court_id.data,
            creator_id=current_user.id,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            max_players=form.max_players.data,
            difficulty=form.difficulty.data
        )
        db.session.add(game)
        db.session.commit()

        # 생성자를 자동으로 참가자로 등록
        participant = GameParticipant(
            game_id=game.id,
            user_id=current_user.id
        )
        db.session.add(participant)
        db.session.commit()
        
        flash('경기가 성공적으로 등록되었습니다.')
        return redirect(url_for('main.index'))
    return render_template('games/create.html', title='경기 등록', form=form)

@bp.route('/games/<int:id>')
def game_detail(id):
    game = Game.query.get_or_404(id)
    return render_template('games/detail.html', title='경기 상세 정보', game=game)

@bp.route('/games/<int:id>/delete', methods=['POST'])
@login_required
def delete_game(id):
    game = Game.query.get_or_404(id)
    if game.creator_id != current_user.id:
        abort(403)  # Forbidden
    
    # 먼저 참가자 정보 삭제
    GameParticipant.query.filter_by(game_id=id).delete()
    
    # 경기 삭제
    db.session.delete(game)
    db.session.commit()
    flash('경기가 삭제되었습니다.')
    return redirect(url_for('main.index'))

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
    
    # 경기장 삭제
    db.session.delete(court)
    db.session.commit()
    flash('경기장이 삭제되었습니다.')
    return redirect(url_for('main.index')) 

@bp.route('/games/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_participation(id):
    game = Game.query.get_or_404(id)
    participant = GameParticipant.query.filter_by(game_id=id, user_id=current_user.id).first()
    
    if not participant:
        flash('해당 경기에 참가하지 않았습니다.', 'error')
        return redirect(url_for('auth.mypage'))
    
    db.session.delete(participant)
    db.session.commit()
    flash('경기 참가가 취소되었습니다.')
    return redirect(url_for('auth.mypage')) 