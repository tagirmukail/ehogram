from app import mongo
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

class RegistrationForm(Form):
    nick = StringField('nick', validators=[Required(), Length(4, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                             'Nickname must have only letters, numbers, dots or underscores')])
    email = StringField('email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Password must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        users = mongo.db.users
        user = users.find_one({'email': field.data})
        if user:
            raise ValidationError('Email alredy registered.')

    def validate_username(self, field):
        users = mongo.db.users
        user = users.find_one({'name': field.data})
        if user:
            raise ValidationError('Nickname alredy in use.')

class LoginForm(Form):
    nick = StringField('nick', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Log in')
