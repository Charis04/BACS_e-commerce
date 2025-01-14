from flask_wtf import FlaskForm  # type: ignore
from wtforms import (  # type: ignore
    StringField, PasswordField, TextAreaField,
    DecimalField, SelectField
)
from wtforms.validators import (  # type: ignore
    DataRequired,
    Email,
    Length,
    NumberRange
)


class BaseForm(FlaskForm):
    class Meta:
        csrf = True


class LoginForm(BaseForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(BaseForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=80)]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)]
    )
    role = SelectField(
        'Role',
        choices=[('buyer', 'Buyer'), ('seller', 'Seller')]
    )


class ProductForm(BaseForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField(
        'Price',
        validators=[DataRequired(), NumberRange(min=0)]
    )


class CartForm(FlaskForm):
    class Meta:
        csrf = False  # Explicitly disable CSRF for cart form
