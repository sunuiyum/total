from total import app, token, sp, username, mysql
import spotipy
import spotipy.util as util
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask.ext.mysql import MySQL
import MySQLdb.cursors
from datetime import datetime

con = mysql.connect()

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
	tracks = results['tracks']['items']
	playlist_dict = []
	for track in tracks:
		track_entry = {
			'title': track['track']['name'],
			'artist': track['track']['artists'][0]['name'],
			'date_added': datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ'),
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

# def insert_playlist_appearance(song, artist, playlist_name, date_added):
	