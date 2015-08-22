from total import app, token, sp, username, mysql
import spotipy
import spotipy.util as util
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask.ext.mysql import MySQL
import MySQLdb.cursors
from datetime import datetime

def get_playlists(service):
	con = mysql.connect()
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
	tracks = results['tracks']['items']
	playlist_dict = {}
	playlist_dict[playlist_name] = []
	for track in tracks:
		track_entry = {
			'title': track['track']['name'],
			'artist': track['track']['artists'][0]['name'],
			'date_added': datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ')
			}
		playlist_dict[playlist_name].append(track_entry)
	return playlist_dict



