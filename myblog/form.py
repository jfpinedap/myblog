from wtforms import (
    Form, BooleanField, StringField, validators, PasswordField,
    TextAreaField
)

class RegistrationForm(Form):
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

class LoginForm(Form):
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

class ForgotForm(Form):
    email = StringField(
        label='Email',
        validators=[
            validators.Length(min=6, max=120),
            validators.Email(),
            validators.InputRequired()
        ]
    )

class CreateBlogForm(Form):
    title = StringField(
        label='Title',
        validators=[
            validators.Length(min=4, max=25),
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
