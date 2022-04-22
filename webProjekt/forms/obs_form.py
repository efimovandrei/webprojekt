from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ObsForm(FlaskForm):
    name = TextAreaField("Заголовок")
    content = TextAreaField("Содержание")
    submit = SubmitField('Применить')

