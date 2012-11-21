# coding: utf-8

import os
import sys
import time
import calendar
import popcorn

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

	args = argparser.parse_args()

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

		message = {
			"time": time,
			"author": author,
			"content": content,
			"channel": args.channel
		}
		popcorn.db.messages.insert(message)

if __name__ == '__main__':
	main()

