#!/usr/bin/env python3
import sys
import time
import telepot
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from memento_client import MementoClient
import re
import urllib

with open('token.txt', 'r') as f:
	token = f.read().strip('\n')
bot = telepot.Bot(token)
answerer = telepot.helper.Answerer(bot)
print ('Started...')
timegate = 'https://archive.fo/timegate/'
mc = MementoClient(timegate_uri=timegate, check_native_timegate=False)
def handle(msg):
	print(telepot.flavor(msg))
	flava = telepot.flavor(msg)
	if (flava == 'chat'):
		content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
		if content_type != 'text':
			return
		command = msg['text'].lower()
		if (command.split(' ')[0] == '/archive' or command.split(' ')[0] == '/archive@archiveisbot'):
			try:
				is_reply = msg['reply_to_message']
			except KeyError:
				pass
			else:
				command = is_reply['text']
	elif (flava == 'inline_query'):
		query_id, form_id, query_string = telepot.glance(msg, flavor='inline_query')
#		print ('Inline Query:', query_id, form_id, query_string)
		return query_string
	else:
		return

def link_handler():
#	content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
	print (handle(msg))
	if on_chat_command:
		uri_rec = re.search("(?P<url>https?://[^\s]+)", on_chat_command())
		query_type = 'chat'
	elif query_string:
		uri_rec = re.search("(?P<url>https?://[^\s]+)", query_string)
		query_type = 'inline'
	else:
		return
	if uri_rec:
		uri = uri_rec.group("url")
		print(uri)
		try:
			archive_uri = mc.get_memento_info(uri).get("mementos").get("last").get("uri")[0]
#				print(uri)
#				print(archive_uri)
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
			return
#		return archive_uri
	if query_type == 'chat':
		return chat_response(msg), archive_uri
	elif query_type == 'inline':
		return inline_response(msg), archive_uri

def chat_response(msg):
	content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
	bot.sendMessage(chat_id, link_handler, reply_to_message=msg_id)

def inline_response(msg):
	def compute():
		archive_json = [InlineQueryResultArticle(
				id='url',
				title=archive_uri,
				input_message_content=InputTextMessageContent(
					message_text=archive_uri
				)
			)]
		return archive_json
	answerer.answer(msg, compute)


#	print(archive_uri)
#		bot.answerInlineQuery(query_id, archive_uri)


bot.message_loop(handle)
while 1:
	time.sleep(10)
