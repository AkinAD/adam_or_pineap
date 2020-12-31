from flask_wtf import FlaskForm
from flask_wtf.html5 import URLField
from wtforms import FileField,SubmitField
from wtforms.validators import url, DataRequired, Optional, optional
from flask_wtf.file import FileField, FileAllowed


#https://flask-wtf.readthedocs.io/en/stable/form.html
# https://pythonhosted.org/Flask-WTF/form.html

class UploadForm(FlaskForm):
    upload = FileField('Custom Upload', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])

class LinkForm(FlaskForm):
    url = URLField('Image Link',validators=[url(),Optional()])

class akinsDataForm(FlaskForm):
    upload = FileField('Custom Upload', validators=[
        FileAllowed(['jpg', 'png'], 'PNG, JPG Images only!')
    ])
    url = URLField('Image Link', validators=[url(), Optional()])
    submit = SubmitField('Submit to Lord Kinny')

