from flask_wtf import FlaskForm
from models import User, Boss
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from wtforms import ValidationError


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    boss_token = StringField('Токен начальника', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован.')

    def validate_boss_token(self, boss_token):
        if boss_token.data:
            boss = Boss.query.filter_by(unique_token=boss_token.data).first()
            if not boss:
                raise ValidationError('Указанный boss_token недействителен. Проверьте правильность токена.')


class RegistrationBossForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = Boss.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован.')