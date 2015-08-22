import spotipy
import spotipy.util as util
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask.ext.mysql import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'the secret key'
app.debug = True

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '300'
app.config['MYSQL_DATABASE_DB'] = 'Total'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

SPOTIPY_CLIENT_ID='d8e879306c5f4f63ac4550069119409c'
SPOTIPY_CLIENT_SECRET='0848a69fb875483b9544bcc3aa409bf3'
SPOTIPY_REDIRECT_URI='http://localhost:5000'
scope = 'user-read-private user-read-email'
username = 'crimsonclear'

token = util.prompt_for_user_token(username, scope=scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)

if token:
	sp = spotipy.Spotify(auth=token)


# def build_api_call(playlist)
# 	tracks = sp.user_playlist_tracks(username, playlist_id=playlist)

# 	for track in tracks:

# 		track_entry = []
# 		track_entry = [
# 			'track': track,
# 			'playlist': playlist,
# 		]
	
import total.views
