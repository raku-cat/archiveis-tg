#!/usr/bin/env python3
import sys
import time
import telepot
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from memento_client import MementoClient
import re
import urllib

TOKEN = open('token.txt', 'r').read()
bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)
print ('Started...')

def handle(msg):
#	print(telepot.flavor(msg))
	flava = telepot.flavor(msg)
	if (flava == 'chat'):
		content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
	elif (flava == 'inline_query'):
		return on_inline_query(msg)
	else:
		return
#	print(content_type, chat_type, chat_id, msg_id)
	if content_type != 'text':
		return
	command = msg['text'].lower()
#	print(msg)
	if (command.split(' ')[0] == '/archive' or command.split(' ')[0] == '/archive@archiveisbot'):
		timegate = 'https://archive.fo/timegate/'
		mc = MementoClient(timegate_uri=timegate, check_native_timegate=False)
		try:
			is_reply = msg['reply_to_message']
		except KeyError:
			pass
		else:
			command = is_reply['text']

		uri_rec = re.search("(?P<url>https?://[^\s]+)", command)
		if uri_rec:
			uri = uri_rec.group("url")
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
				archive_url = url_b.decode('utf8')
				bot.sendMessage(chat_id, archive_url, reply_to_message_id=msg_id)

			else:
				bot.sendMessage(chat_id, archive_uri, reply_to_message_id=msg_id)
		else:
			bot.sendMessage(chat_id, 'No url found, make sure to include http(s)://', reply_to_message_id=msg_id)
def on_inline_query(msg):
	def compute():
		query_id, form_id, query_string = telepot.glance(msg, flavor='inline_query')
#		print ('Inline Query:', query_id, form_id, query_string)
		timegate = 'https://archive.fo/timegate/'
		mc = MementoClient(timegate_uri=timegate, check_native_timegate=False)
		uri_rec = re.search("(?P<url>https?://[^\s]+)", query_string)
		if uri_rec:
			uri = uri_rec.group("url")
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
		archive_uri = [InlineQueryResultArticle(
				id='url',
				title=archive_uri,
				input_message_content=InputTextMessageContent(
					message_text=archive_uri
				)
			)]
		return archive_uri
	answerer.answer(msg, compute)


#	print(archive_uri)
#		bot.answerInlineQuery(query_id, archive_uri)


bot.message_loop(handle)
while 1:
	time.sleep(10)
