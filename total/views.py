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
		cursor = con.cursor()
		cursor.execute("""
			SELECT song_id FROM 
			""")
		return render_template('index.html', playlists=names)