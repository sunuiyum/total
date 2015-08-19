from total import app, token
from flask import Flask, render_template, request, session, redirect, url_for

@app.route("/")
def main():
	if token:
		return render_template('index.html')