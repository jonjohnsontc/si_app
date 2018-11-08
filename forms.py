from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class ArtistForm(FlaskForm):
    artist_name =  StringField('Artist Name (lowercase)')
    submit = SubmitField('Submit')

class SongIDForm(FlaskForm):
    song_id = StringField('Song ID')
    submit = SubmitField('Submit')