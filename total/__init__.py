import spotipy
import spotipy.util as util
from flask import Flask, render_template, request, session, redirect, url_for
from flask.ext.mysql import MySQL

app = Flask(__name__)
app.secret_key = 'the secret key'
app.debug = True

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '300'
app.config['MYSQL_DATABASE_DB'] = '300'
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

class Song(object):
	def __init__(self, id):
		self.id = id
		con = mysql.connect()
		cursor = con.cursor()
		cursor.execute("""
			SELECT song_id FROM song_database WHERE song_id = %s""",
			(str(id),)
			)
		tracked = cursor.fetchone()
		cursor.close()
		if tracked:
			tracked = tracked[0]
		if self.id == tracked:
			self.tracked = True
		else:
			self.tracked = False
		cursor = con.cursor()
		cursor.execute("""
			SELECT song_id FROM blacklist WHERE song_id = %s""",
			(str(id),)
			)
		signed = cursor.fetchone()
		cursor.close()
		if signed:
			signed = signed[0]
		if self.id == signed:
			self.signed = True
		else:
			self.signed = False
		def insert(self):
			if self.tracked == False:
				cursor = con.cursor()
				cursor.execute("""
					INSERT INTO song_database()
					""")

# def build_api_call(playlist)
# 	tracks = sp.user_playlist_tracks(username, playlist_id=playlist)

# 	for track in tracks:

# 		track_entry = []
# 		track_entry = [
# 			'track': track,
# 			'playlist': playlist,
# 		]
	
import total.views
