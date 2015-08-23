#! /Users/Sun-Ui/Code/Total/env/bin/python

import MySQLdb
import MySQLdb.cursors
import re
import spotipy
import spotipy.util as util
from titlecase import titlecase
from datetime import datetime
from unidecode import unidecode
import soundcloud

SPOTIPY_CLIENT_ID='d8e879306c5f4f63ac4550069119409c'
SPOTIPY_CLIENT_SECRET='0848a69fb875483b9544bcc3aa409bf3'
SPOTIPY_REDIRECT_URI='http://localhost:5000'
scope = 'user-read-private user-read-email'
username = 'crimsonclear'

token = util.prompt_for_user_token(username, scope=scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)

if token:
	sp = spotipy.Spotify(auth=token)

con = MySQLdb.connect(host="localhost", user="root", passwd="300", db="Total")

client = soundcloud.Client(
	client_id='e0947da1121e6215e4d2f1ff5c544232',
	client_secret='a3085f7a42816cc131e4884f8bc93f10',
	redirect_uri = 'http://localhost:5000',
	refresh_token='https://api.soundcloud.com/oauth2/token',
	username='sunuiyum',
	password='UiJung96018096'
	)

def clean_string(string):
	regex = re.compile("\s*\(?\[?[Ff]eat\.", flags=re.I)
	test = regex.split(string)[0]
	word_blacklist = [' - Radio Edit', '(Radio Edit)', '(Original Mix)', ' - Original Mix', '(Radio Mix)', ' - Original Mix']
	for word in word_blacklist:
		if word in test:
			test = test.strip(word)
	return test

def get_playlists(service):
	dict_cursor = con.cursor(MySQLdb.cursors.DictCursor)
	dict_cursor.execute("""
		SELECT playlist_name, playlist_uri, playlist_owner_id FROM playlist_database
		WHERE playlist_service = %s""",
		(str(service),)
		)
	user_playlists = dict_cursor.fetchall()
	return user_playlists

def get_playlist_tracks(owner_id, playlist_id, playlist_name):
	results = sp.user_playlist(owner_id, playlist_id, fields="tracks")
	tracks = results['tracks']
	playlist_dict = []
	items = tracks['items']
	for item in items:
		track_entry = {
			'title': item['track']['name'],
			'artist': item['track']['artists'][0]['name'],
			'date_added': datetime.strptime(item['added_at'], '%Y-%m-%dT%H:%M:%SZ'),
			'playlist': playlist_name
			}
		playlist_dict.append(track_entry)
	while tracks['next']:
		tracks = sp.next(tracks)
		items = tracks['items']
		for item in items:
			track_entry = {
				'title': item['track']['name'],
				'artist': item['track']['artists'][0]['name'],
				'date_added': datetime.strptime(item['added_at'], '%Y-%m-%dT%H:%M:%SZ'),
				'playlist': playlist_name
				}
			playlist_dict.append(track_entry)

	return playlist_dict

def get_song_playlists(song, artist):
	cursor = con.cursor()
	cursor.execute("""
		SELECT song_id FROM song_database
		WHERE song = %s AND artist = %s""",
		(song, artist)
		)
	song_id = int(cursor.fetchone()[0])
	cursor.execute("""
		SELECT playlist_id FROM playlist_performance
		WHERE song_id = %s""",
		(song_id,)
		)
	playlist_list = list(cursor.fetchall())
	for x in range(0, len(playlist_list)):
		playlist_list[x] = playlist_list[x][0]
	return playlist_list

def check_blacklist(artist, blacklist):
	if artist.upper() in blacklist:
		blacklisted = 1
	else:
		blacklisted = 0
	return blacklisted

def get_song_id(song, artist):
	cursor = con.cursor()
	cursor.execute("""
		SELECT song_id FROM song_database
		WHERE song = %s AND artist = %s""",
		(song, artist)
		)
	song_id = int(cursor.fetchone()[0])
	return song_id

cursor = con.cursor()
cursor.execute("""
	SELECT artist FROM blacklist
	""")
blacklist = cursor.fetchall()
cursor.close()
blacklist = list(blacklist)
for x in range(0, len(blacklist)):
	blacklist[x] = str(blacklist[x][0])

playlists = get_playlists('Spotify')
for playlist in playlists:
	tracks = get_playlist_tracks(playlist['playlist_owner_id'], playlist['playlist_uri'], playlist['playlist_name'])
	playlist = playlist['playlist_name']
	cursor = con.cursor()
	cursor.execute("""
		SELECT song FROM song_database
		""")
	song_dict = cursor.fetchall()
	cursor.close()
	song_dict = list(song_dict)
	for x in range(0, len(song_dict)):
		song_dict[x] = str(song_dict[x][0])
	for track in tracks:
		cursor = con.cursor()
		song = titlecase(unidecode(clean_string(track['title'])))
		artist = unidecode(track['artist'])
		cursor.execute("""
			SELECT playlist_id FROM playlist_database
			WHERE playlist_name = %s""",
			(playlist,)
			)
		playlist_id = int(cursor.fetchone()[0])
		cursor.close()
		cursor = con.cursor()
		if song not in song_dict:
			blacklisted = check_blacklist(artist, blacklist)
			cursor.execute("""
				INSERT IGNORE INTO song_database (song, artist, blacklisted)
				VALUES (%s, %s, %s)""",
				(song, artist, blacklisted)
				)
			con.commit()
			song_id = get_song_id(song, artist)
			cursor.close()
			cursor = con.cursor()
			cursor.execute("""
				INSERT INTO playlist_performance (playlist_id, song_id, date_added)
				VALUES (%s, %s, %s)""",
				(playlist_id, song_id, track['date_added'])
				)
			con.commit()
			cursor.close()
		elif song in song_dict:
			cursor.execute("""
				SELECT artist FROM song_database
				WHERE song = %s""",
				(song,)
				)
			song_artists = list(cursor.fetchall())
			for x in range(0, len(song_artists)):
				song_artists[x] = song_artists[x][0]
			if artist in song_artists:
				#Figure out if this playlist appearance has already been recorded 
				playlist_list = get_song_playlists(song, artist)
				if playlist_id in playlist_list:
					cursor.close()
				else: 
					song_id = get_song_id(song, artist)
					cursor.execute("""
						SELECT playlist_id FROM playlist_database
						WHERE playlist_name = %s""",
						(playlist,)
						)
					playlist_id = int(cursor.fetchone()[0])
					cursor.close()
					cursor = con.cursor()
					cursor.execute("""
						INSERT INTO playlist_performance (playlist_id, song_id, date_added)
						VALUES (%s, %s, %s)""",
						(playlist_id, song_id, track['date_added'])
						)
					con.commit()
					cursor.close()
			else:
				blacklisted = check_blacklist(artist, blacklist)
				cursor.execute("""
					INSERT INTO song_database (song, artist, blacklisted)
					VALUES (%s, %s, %s)""",
					(song, artist, blacklisted)
					)
				con.commit()
				song_id = get_song_id(song, artist)
				cursor.execute("""
					SELECT playlist_id FROM playlist_database
					WHERE playlist_name = %s""",
					(playlist,)
					)
				playlist_id = int(cursor.fetchone()[0])
				cursor.close()
				cursor = con.cursor()
				cursor.execute("""
					INSERT INTO playlist_performance (playlist_id, song_id, date_added)
					VALUES (%s, %s, %s)""",
					(playlist_id, song_id, track['date_added'])
					)
				con.commit()
				cursor.close()

for playlist in playlists:
	#tracks is the list of songs that are currently on the playlist
	tracks = get_playlist_tracks(playlist['playlist_owner_id'], playlist['playlist_uri'], playlist['playlist_name'])
	cursor = con.cursor()
	cursor.execute("""
		SELECT playlist_id FROM playlist_database
		WHERE playlist_name = %s""",
		(playlist['playlist_name'],)
		)
	playlist_id = int(cursor.fetchone()[0])
	#recorded_list is the list of songs the database BELIEVES are currently on the playlist
	cursor.execute("""
		SELECT song_id FROM playlist_performance
		WHERE playlist_id = %s AND date_removed = NULL""",
		(playlist_id,)
		)
	recorded_list = list(cursor.fetchall())
	for x in range(0, len(recorded_list)):
		recorded_list[x] = recorded_list[x][0]
	track_titles = []
	for x in range(0, len(tracks)):
	    track_titles.append(tracks[x]['title'])
	for item in recorded_list:
		cursor.execute("""
			SELECT song FROM song_database
			WHERE song_id = %s""",
			(item,)
			)
		song = str(cursor.fetchone()[0])
		#if the song is in "tracks", the database is right
		if song in track_titles:
			cursor.close()
		#if the song isn't in "tracks", the song's been removed from the playlist
		elif song not in track_titles:
			today = datetime.now()
			cursor.execute("""
				UPDATE playlist_performance
				SET date_removed = %s
				WHERE song_id = %s AND playlist_id = %s""",
				(today, item, playlist_id)
				)
			cursor.commit()
			cursor.close()

#Get list of users
cursor = con.cursor()
cursor.execute("""
	SELECT sc_id FROM tastemaker_database
	""")
sc_users = cursor.fetchall()

con.close()