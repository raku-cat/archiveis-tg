#!/usr/bin/env python3
import sys
import time
import telepot
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from memento_client import MementoClient
import re
import requests
import random

with open('token.txt', 'r') as f:
	token = f.read().strip('\n')
bot = telepot.Bot(token)
answerer = telepot.helper.Answerer(bot)

def on_chat_command(msg):
	content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
	if content_type != 'text':
		return
	command = msg['text'].lower()
	if (command.split(' ')[0] == '/archive' or command.split(' ')[0] == '/archive@archiveisbot'):
		print('Valid command from ' + str(chat_id))
		try:
			is_reply = msg['reply_to_message']
		except KeyError:
			pass
		else:
			command = is_reply['text']
	else:
		return
	print('Responding to ' + str(chat_id))
	bot.sendMessage(chat_id, link_handler(command), reply_to_message_id=msg_id)

def on_inline_query(msg):
	query_id, form_id, query_string = telepot.glance(msg, flavor='inline_query')
#	print(query_string)
	print('Query ' + query_id + ' recieved')
	archive_uri =link_handler(query_string)
	if archive_uri == None:
		return
	def compute():
		if '.fo' in archive_uri:
			archive_json = [InlineQueryResultArticle(
					id='url', title=archive_uri,
					input_message_content=InputTextMessageContent(
						message_text=archive_uri),
					)]
		elif '.is' in archive_uri:
			timegate = 'https://archive.fo/timemap/'
			mc = MementoClient(timegate_uri=timegate, check_native_timegate=False)
			timemap = mc.get_memento_info(query_string).get('timegate_uri')
			hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',}
			r = requests.get(timemap, headers=hdr)
			archive_map = r.text
			map_list = re.findall('\<(.*?)\>', archive_map)[2:-1]
			date_list= re.findall('datetime=\"(.+)\"', archive_map)
			print(len(map_list))
			print(len(date_list))
			archive_json = []
			if len(map_list) > 50:
				map_list = re.findall('\<(.*?)\>', archive_map)[2:50]
				date_list = re.findall('/datetime=\"(.+)\"/', archive_map)[0:50]
			for x, y in zip(map_list, date_list):
#				for y in date_list:
					rnint = str(random.randint(1,3000))
					archive_json.append(InlineQueryResultArticle(
						id=rnint, title=y,
					input_message_content=InputTextMessageContent(
					message_text=x),
					cache_time=None
				))
		else:
			exit()
		print('Sending query response\n')
		return archive_json
	answerer.answer(msg, compute)

def link_handler(link):
	uri_rec = re.search("(?P<url>https?://[^\s]+)", link)
	if uri_rec:
		print('Url found')
		uri = uri_rec.group("url")
#		print(uri)
		timegate = 'https://archive.fo/timegate/'
		mc = MementoClient(timegate_uri=timegate, check_native_timegate=False)
		try:
			archive_uri = mc.get_memento_info(uri).get("mementos").get("last").get("uri")[0]
#			print(uri)
#			print(archive_uri)
			print('Archive is ' + archive_uri)
		except:
			url = 'https://archive.fo/submit/'
			values = { 'url' : uri }
			headers = { 'User-Agent' : 'Telegram archive bot - https://github.com/raku-cat/archiveis-tg' }
			r = requests.post(url, data=values, headers=headers)
			response = r.text
#			print(response)
			archive_uri = response.split('"')[1]
			print('Archive creation sucessful')
		else:
			return archive_uri
	else:
		return 'No valid URL found'
	return archive_uri

bot.message_loop({'chat': on_chat_command,
		'inline_query': on_inline_query,
		'edited_chat': on_chat_command,
		},
		run_forever='Started...')
