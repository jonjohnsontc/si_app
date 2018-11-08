import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import numpy as np
import pandas as pd

# Loading in table
main_song_list = pd.read_csv('~/dev/SWI_2/Songwriter_Index/data/main_wfeats.csv', index_col='song_id')
main_song_list.drop('Unnamed: 0', 1, inplace=True)

bp = Blueprint('artist_finder', __name__, url_prefix='/artist')


@bp.route('/find_song/<SongID>', methods=('GET', 'POST'))
def song_finder(song_list=main_song_list):
    '''
    Retreives a list of valid song titles and corresponding id's given an artist name.
    Artist name should be given in lowercase.
    '''

    # render template here? http://flask.pocoo.org/docs/1.0/tutorial/views/
    artist_name = request.form['artist_name']
    results = song_list[['song_title']][song_list['artist_name'].apply(lambda x: x.lower()) == artist_name]
    if results.empty == True:
        return "Please try searching for another artist"
    else:
        return results.rename({'song_title':'Songs'}, axis=1).to_json(orient='columns')
