# coding: utf-8

from popcorn import db, config
from bottle import request, redirect, abort, static_file
import time
import pymongo
import bottle
import jinja2
import bson

app = bottle.Bottle()
jinja2_env = jinja2.Environment(loader=jinja2.PackageLoader("popcorn", "templates"))

def render_template(_tpl, **kwargs):
	template = jinja2_env.get_template(_tpl)
	return template.render(kwargs)

def convert_time_to_string(d):
	d["time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(d["time"]))
	return d

@app.route("/static/<path:path>")
def static(path):
	return static_file(path, root="popcorn/static")

@app.route("/")
def index():
	popcorns = db.popcorns.find().sort("time", pymongo.DESCENDING)
	popcorns = map(convert_time_to_string, popcorns)

	return render_template("index.html", popcorns=popcorns)

@app.route("/logs/<channel>")
@app.route("/logs")
def show_logs(channel="#jupis"):
	if channel[0] != '#':
		channel = '#' + channel
	
	try:
		start_time = int(request.params["start"])
		end_time = int(request.params["end"])

		messages = db.messages.find({"channel": channel, "time": {"$lt": end_time, "$gt": start_time}}).sort("time", pymongo.DESCENDING)
	except (ValueError, KeyError):
		messages = db.messages.find({"channel": channel}).sort("time", pymongo.DESCENDING).limit(100)
	messages = map(convert_time_to_string, messages)

	return render_template("messages.html", messages=messages, channel=channel)

@app.route("/popcorns/<popcorn>")
def popcorn_show(popcorn):
	try:
		popcorn = bson.ObjectId(popcorn)
	except:
		abort(404, "Popcorn not found")

	popcorn = db.popcorns.find_one({"_id": popcorn})
	if not popcorn:
		abort(404, "Popcorn not found")

	messages = db.messages.find({"channel": popcorn["channel"], "time": {"$lt": popcorn["end"], "$gt": popcorn["start"]}}).sort("time", pymongo.ASCENDING)
	messages = map(convert_time_to_string, messages)

	return render_template("popcorns/show.html", messages=messages, popcorn=popcorn)

@app.route("/popcorns")
def popcorn_index():
	redirect("/")

if __name__ == '__main__':
	import wsgiref.simple_server
	httpd = wsgiref.simple_server.make_server('127.0.0.1', 8080, app)

	print("Serving HTTP on 127.0.0.1:8080...")
	httpd.serve_forever()
