from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class SearchForm(Form):
    search_term = StringField('')
    submit = SubmitField('Search')

