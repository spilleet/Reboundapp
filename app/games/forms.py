from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError

class GameForm(FlaskForm):
    court_id = SelectField('경기장', coerce=int, validators=[DataRequired()])
    date = DateField('날짜', validators=[DataRequired()])
    start_time = TimeField('시작 시간', validators=[DataRequired()])
    end_time = TimeField('종료 시간', validators=[DataRequired()])
    max_players = IntegerField('최대 인원', validators=[
        DataRequired(),
        NumberRange(min=2, max=20, message='인원은 2명에서 20명 사이여야 합니다.')
    ])
    difficulty = SelectField('난이도', choices=[
        ('beginner', '초급'),
        ('intermediate', '중급'),
        ('advanced', '고급')
    ], validators=[DataRequired()])
    submit = SubmitField('등록하기')

    def validate_end_time(self, field):
        if self.start_time.data and field.data:
            if field.data <= self.start_time.data:
                raise ValidationError('종료 시간은 시작 시간보다 늦어야 합니다.') 