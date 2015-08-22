from total import app, token, sp, username
# from models import get_playlists
import models
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

@app.route("/")
def main():
	if token:
		return render_template('index.html')

@app.route("/playlists")
def show_playlists():
	if token:
		playlists = get_playlists('Spotify')
		playlist_dict = []
		for playlist in playlists:
			playlist_dict.append(get_playlist_tracks(playlist['playlist_owner_id'], playlist['playlist_uri'], playlist['playlist_name']))
		return render_template('index.html', playlists=names)