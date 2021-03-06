#!/usr/bin/env python3
import sys
import time
import telepot
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from memento_client import MementoClient
import re
import requests
import random
import datetime
from bs4 import BeautifulSoup

global delay
delay = datetime.datetime.now()
with open(sys.path[0] + '/token.txt', 'r') as f:
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
    bot.sendChatAction(chat_id, 'typing')
    handled_link = link_handler(command)
    result_type = type(handled_link)
#   print(result_type)
    if result_type == str:
        bot.sendMessage(chat_id, handled_link, reply_to_message_id=msg_id)
    elif result_type == tuple:
        keyboard = handled_link[1]
        handled_link = handled_link[0]
        bot.sendMessage(chat_id, handled_link, reply_to_message_id=msg_id, reply_markup=keyboard)
    else:
        return
    print('Responding to ' + str(chat_id))

def on_inline_query(msg):
    query_id, form_id, query_string, offset = telepot.glance(msg, flavor='inline_query', long=True)
#    print(msg)
#    print(type(offset))
    print('Query ' + query_id + ' recieved')
    try:
        archive_uri, keyboard = link_handler(query_string)
    except:
        archive_uri = ''
    uri = query_string
    next_offset = int(offset) if offset != '' else 0
    def compute():
        offset = next_offset
        if '.fo' in archive_uri:
            archive_json = [InlineQueryResultArticle(
                    id='url', title=archive_uri,
                    input_message_content=InputTextMessageContent(
                        message_text=archive_uri),
                    )]
        elif '.is' in archive_uri:
            timemap = 'https://archive.fo/timemap/' + query_string
            r = requests.get(timemap)
            archive_map = r.text
            map_list = re.findall('\<(.*?)\>', archive_map)[2:-1]
            date_list = re.findall('datetime=\"(.+)\"', archive_map)
#            print(len(map_list))
#            print(len(date_list))
            archive_json = []
            if len(map_list) > 50:
                if offset:
                    if len(map_list[offset:]) > 50:
                        map_list = re.findall('\<(.*?)\>', archive_map)[2 + offset:offset + 50]
                        date_list = re.findall('datetime=\"(.+)\"', archive_map)[offset:]
                else:
                    map_list = re.findall('\<(.*?)\>', archive_map)[2:50]
#               print(len(map_list))
#               print(len(date_list))
                offset = str(int(offset) + 51)
            rnint = random.sample(range(5000), 50)
            for x, y, z in zip(map_list, date_list, rnint):
                    archive_json.append(InlineQueryResultArticle(
                        id=str(z), title=y,
                    input_message_content=InputTextMessageContent(
                    message_text=x),
                ))
        else:
            exit()
        print('Sending query response\n')
        return {'results': archive_json, 'next_offset': offset}
#    return
    answerer.answer(msg, compute)

def on_callback_query(msg):
    query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
#    print(msg)
#    print(query_data)
    print('Recieved query ' + query_id)
    url = msg['message']['reply_to_message']['text'].split(' ')[1]
    msg_idf = telepot.message_identifier(msg['message'])
    callback_text = ''
    global delay
    if query_data == 'save':
        if delay != '':
            if datetime.datetime.now() > delay:
                r = requests.get('https://archive.fo/')
                html = r.text
                soup = BeautifulSoup(html, 'lxml')
                submitid = soup.find('input').get('value')
                headers = { 'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' }
                values = { 'submitid': submitid, 'url': url, 'anyway': '1' }
                r = requests.post('https://archive.fo/submit/', data=values, headers=headers)
                uri = r.text
                archive_uri = uri.split('"')[1]
                delay = datetime.datetime.now() + datetime.timedelta(minutes=3)
                if 'archive.fo' in archive_uri:
                    pass
                else:
                    callback_text = 'Something went wrong, let @raku_cat know'
            else:
                callback_text = 'Saving on cooldown, please try again in a few miniutes.'
    else:
        uri = msg['message']['text']
        foo, keyboard = link_handler(url)
        dt = uri.split('/')[3]
        dt = datetime.datetime.strptime(dt, '%Y%m%d%H%M%S')
        timegate = 'https://archive.fo/timegate/'
        mc = MementoClient(timegate_uri=timegate, check_native_timegate=False)
        if query_data == 'back':
            try:
                archive_uri = mc.get_memento_info(url, dt).get('mementos').get('prev').get('uri')[0]
            except AttributeError:
                callback_text = 'No older archives or something went wrong.'
        elif query_data == 'next':
            try:
               archive_uri = mc.get_memento_info(uri, dt).get('mementos').get('next').get('uri')[0]
            except AttributeError:
               callback_text = 'No newer archives or something went wrong.'
    try:
        bot.editMessageText(msg_idf, archive_uri)
    except:
        pass
    try:
        bot.editMessageText(msg_idf, archive_uri, reply_markup=keyboard)
    except:
        pass
    bot.answerCallbackQuery(query_id, text=callback_text)
    print('Responding to callback ' + query_id)

def link_handler(link):
    try:
        link = link.split(' ')[1]
    except IndexError:
        pass
    #print(str_link)
    uri_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    uri_rec = uri_regex.search(link)
    #uri_rec = re.search("(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", link)
    #print(uri_rec)
    #print(uri_regex)
    #print(link)
    if uri_rec:
        print('Url found')
        uri = uri_rec.group(0)
        print(uri)
        timegate = 'https://archive.fo/timegate/'
        mc = MementoClient(timegate_uri=timegate, check_native_timegate=False)
        try:
            archive_uri = mc.get_memento_info(uri).get("mementos").get("last").get("uri")[0]
#            print(uri)
#           print(archive_uri)
            print('Archive is ' + archive_uri)
        except AttributeError:
            archive_uri = archive_create(uri)
            return archive_uri
        except NameError:
            print('Sum happen')
            return('Something went wrong, let @raku_cat know')
        else:
            pass
    else:
        return 'No valid URL found'
    if 'archive.fo' in archive_uri:
#       print(archive_uri)
        return archive_uri
    elif 'archive.is' in archive_uri:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Force save page', callback_data='save')],
                    [InlineKeyboardButton(text='← Prior', callback_data='back'), InlineKeyboardButton(text='Next →', callback_data='next')],
                    [InlineKeyboardButton(text='History', switch_inline_query_current_chat=uri)],
                ])
        return archive_uri, keyboard
    elif 'trans' in archive_uri:
        archive_uri = mc.get_memento_info(uri).get("timegate_uri")
        print('Sent weird api deal')
        return(archive_uri)
    else:
        print('^No it wasn\'t')
        return 'Something went wrong, let @raku_cat know'

def archive_create(uri):
    url = 'https://archive.fo/submit/'
    values = { 'url': uri }
    headers = { 'User-Agent' : 'Telegram archive bot - https://github.com/raku-cat/archiveis-tg/' }
    r = requests.post(url, values, headers)
    response = r.text
#    print(response)
    archive_uri = response.split('"')[1]
    if 'archive.fo' not in archive_uri:
        print('Archive creation failed')
        return('Something went wrong, let @raku_cat know')
    else:
        print('Archive creation sucessful')
        return archive_uri

bot.message_loop({'chat': on_chat_command,
        'inline_query': on_inline_query,
        'edited_chat': on_chat_command,
        'callback_query': on_callback_query,
        },
        run_forever='Started...')
