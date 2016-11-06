#!/usr/bin/env python3
import sys
import time
import telepot
from memento_client import MementoClient
import re
import urllib

TOKEN = open('token.txt', 'r').read()
bot = telepot.Bot(TOKEN)
print ('Started...')

def handle(msg):
	content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
	print(content_type, chat_type, chat_id, msg_id)
	if content_type != 'text':
		return
	command = msg['text'].lower()
	if (command.split(' ')[0] == '/archive' or command.split(' ')[0] == '/archive@archiveisbot'):
		timegate = 'https://archive.fo/timegate/'
		mc = MementoClient(timegate_uri=timegate, check_native_timegate=False)
		uri_rec = re.search("(?P<url>https?://[^\s]+)", command)
		if uri_rec:
			uri = uri_rec.group("url")
			try:
				archive_uri = mc.get_memento_info(uri).get("mementos").get("last").get("uri")[0]
#				print(uri)
#				print(archive_uri)
			except:
				url = 'https://archive.fo/submit/'
				user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
				values = {'submitid' : '7XIs5VZpPiy4FZ%2FYVRZaI4RfX6ZhY11qJOFbVY527hjhC9YNC72ot4NbOvO7vPo1',
					'url' : uri}
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

bot.message_loop(handle)
while 1:
	time.sleep(10)
