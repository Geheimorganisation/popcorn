# coding: utf-8

import json
import os
import pymongo
from warnings import warn

config = {}
try:
	try:
		config_file = os.environ["POPCORN_CONF"]
	except KeyError:
		config_file = "popcorn.conf"
	with open(config_file) as fh:
		config = json.load(fh)
	del config_file
except (IOError, ValueError):
	warn("I need configuration!")

db = pymongo.Connection()["popcorn"]
try:
	_db_config = {
		"url": "mongodb://127.0.0.1",
		"name": "popcorn"
	}
	_db_config.update(config.get("database", {}))
	db = pymongo.Connection(_db_config["url"])[_db_config["name"]]
	del _db_config
except pymongo.errors.AutoReconnect:
	warn("I need database!")

db.messages.ensure_index([("channel", 1), ("time", -1)])

