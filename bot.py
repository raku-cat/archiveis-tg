#!/usr/bin/env python3
import sys
import time
import telepot
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from memento_client import MementoClient
import re
import urllib
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
		query_type = 'chat'
		try:
			is_reply = msg['reply_to_message']
		except KeyError:
			pass
		else:
			command = is_reply['text']
	else:
		return
	bot.sendMessage(chat_id, link_handler(command), reply_to_message_id=msg_id)

def on_inline_query(msg):
	query_id, form_id, query_string = telepot.glance(msg, flavor='inline_query')
	query_type = 'inline'
	command = None
	def compute():
		timemap = mc.get_memento_info().get('timegate_uri')
#                       hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',}
#                       req = urllib.request.Request(timemap, headers=hdr)
#                       archive_map = urllib.request.urlopen(req).read()
#                       map_list = re.findall(b'\<(.*?)\>', archive_map)[2:-1]
#                       map_decode = [x.decode('utf-8') for x in map_list]
#                       print(archive_uri)
#                       archive_json = []
#                       for x in map_decode:
#                               rnint = str(random.randint(1,30000))
#                               archive_json.append(InlineQueryResultArticle(
#                                       id=rnint, title=x,
#                                       input_message_content=InputTextMessageContent(
#                                               message_text=x)
#                               ))
#                       print(archive_json)
#                       return archive_json
#               answerer.answer(msg, compute)



def link_handler(linkh):
	uri_rec = re.search("(?P<url>https?://[^\s]+)", linkh)
	if uri_rec:
		uri = uri_rec.group("url")
#		print(uri)
		timegate = 'https://archive.fo/timegate/'
		mc = MementoClient(timegate_uri=timegate, check_native_timegate=False)
		try:
			archive_uri = mc.get_memento_info(uri).get("mementos").get("last").get("uri")[0]
#			print(uri)
#			print(archive_uri)
		except:
			url = 'https://archive.fo/submit/'
			user_agent = 'Telegram archive bot - https://github.com/raku-cat/archiveis-tg'
			values = {'url' : uri}
			headers = { 'User-Agent' : user_agent }
			data = urllib.parse.urlencode(values)
			data = data.encode('utf8')
			req = urllib.request.Request(url, data, headers)
			response = urllib.request.urlopen(req)
			page_out = response.read()
			url_b = page_out.split(b'"')[1]
			archive_uri = url_b.decode('utf8')
		else:
			pass
	else:
		return
	return archive_uri

bot.message_loop({'chat': on_chat_command,
		'inline_query': on_inline_query,
		},
		run_forever='Started...')
