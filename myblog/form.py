import secrets
from datetime import timedelta
from wtforms.csrf.session import SessionCSRF
from wtforms import (
    Form, BooleanField, StringField, validators, PasswordField,
    TextAreaField, IntegerField
)

from myblog import SECRET_TOKEN


class MyBaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = SECRET_TOKEN
        csrf_time_limit = timedelta(minutes=30)


class RegistrationForm(MyBaseForm):
    username = StringField(
        label='Username',
        validators=[
            validators.Length(min=4, max=25),
            validators.InputRequired()
        ]
    )
    email = StringField(
        label='Email',
        validators=[
            validators.Length(min=6, max=120),
            validators.Email(),
            validators.InputRequired()
        ]
    )
    password = PasswordField(
        label='Password',
        validators=[
            validators.Length(min=4, max=20),
            validators.InputRequired(),
            validators.EqualTo('confirm', message='Passwords must match')
        ]
    )
    confirm = PasswordField('Repeat password')


class LoginForm(MyBaseForm):
    username = StringField(
        label='Username',
        validators=[
            validators.InputRequired()
        ]
    )
    password = PasswordField(
        label='Password',
        validators=[
            validators.InputRequired()
        ]
    )


class ForgotForm(MyBaseForm):
    email = StringField(
        label='Email',
        validators=[
            validators.Length(min=6, max=120),
            validators.Email(),
            validators.InputRequired()
        ]
    )


class CreateBlogForm(MyBaseForm):
    title = StringField(
        label='Title',
        validators=[
            validators.Length(min=4, max=50),
            validators.InputRequired()
        ]
    )
    body = TextAreaField(
        label='Body',
        validators=[
            validators.InputRequired()
        ]
    )
    public = BooleanField(
        label='Public'
    )


class CreateCommentForm(MyBaseForm):
    text = StringField(
        label='Text',
        validators=[
            validators.Length(min=4, max=255),
            validators.InputRequired()
        ]
    )


class DeleteBlogForm(MyBaseForm):
    pass


class DeleteCommentForm(MyBaseForm):
    pass