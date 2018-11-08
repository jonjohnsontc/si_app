import numpy as np
import pandas as pd
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .forms import ArtistForm, SongIDForm

# Loading in recommender 
with open('/Users/jonjohnson/dev/SWI_2/Songwriter_Index/pickle/cos_sim_mat_g.npy', 'rb') as f:
    cos_sim_mat = np.load(f)

# Loading in primary song tables
pd_song_svd = pd.read_csv('/Users/jonjohnson/dev/SWI_2/Songwriter_Index/data/main_songs_svdg.csv', index_col='song_id')
main_song_list = pd.read_csv('/Users/jonjohnson/dev/SWI_2/Songwriter_Index/data/main_wfeats.csv', index_col='song_id')
main_song_list.drop('Unnamed: 0', 1, inplace=True)

# Loading in lookup tables
song_id_name = dict(zip(main_song_list.index, main_song_list['song_title']))
song_id_artist = dict(zip(main_song_list.index, main_song_list['artist_name']))
song_cosine_id = dict(zip(pd_song_svd.index, range(pd_song_svd.shape[0])))
song_cosine_idr = dict(zip(range(pd_song_svd.shape[0]), pd_song_svd.index))

bp = Blueprint('home', __name__, url_prefix='/')


@bp.route('/', methods=['GET', 'POST'])
def home_page():
    rec_search = SongIDForm()
    
    # for searching song ids
    if rec_search.is_submitted():
        return redirect(url_for('home.get_recs_da', song_id=rec_search.song_id._value()))
    return render_template('base.html', rec_form=rec_search)


@bp.route('/find_song/', methods=['GET', 'POST'])
def find_song():
    song_search = ArtistForm()

    if song_search.is_submitted():
        return redirect(url_for('home.song_finder', artist_name=song_search.artist_name._value()))
    return render_template('find_song.html', song_form=song_search)


@bp.route('/songs/', methods=['GET', 'POST'])
def song_finder(song_list=main_song_list):
    artist_name = request.args.get('artist_name', None)
    results = song_list[['song_title']][song_list['artist_name'].apply(lambda x: x.lower()) == artist_name]
    if results.empty == True:
        return "Please try searching for another artist"
    else:
        return results.rename({'song_title':'Songs'}, axis=1).to_html()
        # render_template('artist.html', results=results.rename({'song_title':'Songs'}, axis=1).to_html())
        # results.rename({'song_title':'Song'}, axis=1).to_json(orient='columns')
    

def feat_sim_da(song_id, k=10, song_db=main_song_list, cos_sim_mat=cos_sim_mat):
    artist_id = song_db.loc[song_id, 'artist_id']
    artist_songs = song_db.index[song_db['artist_id'] == artist_id].drop(song_id)
    top_songs_feat = np.argsort(cos_sim_mat[song_cosine_id[song_id]])[-2:-(k+12):-1]
    top_songs_feat_sim = np.sort(cos_sim_mat[song_cosine_id[song_id]])[-2:-(k+12):-1]
    return top_songs_feat, top_songs_feat_sim, artist_songs


@bp.route('/recs/', methods=['GET', 'POST'])
def get_recs_da(k=10, song_db=main_song_list, cos_sim_mat=cos_sim_mat):
    try:
        song_id = request.args.get('song_id', None)
        top_songs_feat, top_songs_feat_sim, artist_songs = feat_sim_da(song_id, k, main_song_list, cos_sim_mat)
        recs = [
            [song_id_name[song_cosine_idr[x]] for x in top_songs_feat],
            [song_id_artist[song_cosine_idr[x]] for x in top_songs_feat],
            [song_cosine_idr[x] for x in top_songs_feat],
            list(top_songs_feat_sim)
        ]

        recs = pd.DataFrame(recs, index=['Song Name', 'Artist', 'Song ID', 'Similarity']).T
        recs.set_index('Song ID', inplace=True)

        for song in artist_songs:
            if song in recs.index:
                recs.drop(song, inplace=True)

        recs.reset_index(inplace=True)
        return recs.head(k).to_html()
        # recs.head(k).to_json(orient='columns')
    except:
        return 'No results available for that id. Please refer to the Artist Finder for a list of valid ids.'