# coding: utf-8

import os
import sys
import time
import calendar
import popcorn
import pymongo

def normalize_author(author):
	if author[0] in ['@', '+', '~']:
		return author[1:]
	return author

def parse_weechat_time(timestr):
	timestruct = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
	return calendar.timegm(timestruct)

def main():
	import argparse

	argparser = argparse.ArgumentParser(description="Read IRC logs into the database")
	argparser.add_argument('-c', '--channel', default=None)
	argparser.add_argument('-u', '--update', default=False, action='store_true')

	args = argparser.parse_args()
	if args.update:
		last_entry = popcorn.db.messages.find({"channel": args.channel}).sort("time", pymongo.DESCENDING).limit(1)
		if not last_entry.count():
			last_entry = 0
		else:
			last_entry = last_entry[0]["time"]

	for line in sys.stdin:
		line = line.strip()
		try:
			time, author, content = line.split("\t", 2)
		except ValueError:
			continue
		if author in [ '<--', ' *', '-->', '', '--']:
			continue
		time = parse_weechat_time(time)
		author = normalize_author(author)

		if args.update and time <= last_entry:
			continue

		message = {
			"time": time,
			"author": author,
			"content": content,
			"channel": args.channel
		}
		popcorn.db.messages.insert(message)

if __name__ == '__main__':
	main()

