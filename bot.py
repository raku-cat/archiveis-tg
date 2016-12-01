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
        pass
    try:
        if archive_uri == '':
            return
    except:
        return
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
            timegate = 'https://archive.fo/timemap/'
            mc = MementoClient(timegate_uri=timegate, check_native_timegate=False)
            timemap = mc.get_memento_info(query_string).get('timegate_uri')
            print(timemap)
            print( repr(timemap))
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; Nexus 6P Build/NBD91P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2919.3 Mobile Safari/537.36'}
            r = requests.get(timemap, headers)
            print(r)
            archive_map = r.text
            print(archive_map)
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
    return
    answerer.answer(msg, compute)

def on_callback_query(msg):
    query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
#    print(msg)
#    print(query_data)
    print('Recieved query ' + query_id)
    url = msg['message']['reply_to_message']['text'].split(' ')[1]
    msg_idf = telepot.message_identifier(msg['message'])
    callback_text = ''
    if query_data == 'save':
        url = msg['message']['reply_to_message']['text'].split(' ')[1]
        msg_idf = telepot.message_identifier(msg['message'])
        archive_uri_ = archive_create(url)
        if 'archive.fo' not in archive_uri_:
            callback_text = archive_uri_
        else:
            archive_uri = archive_uri_
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
    uri_rec = re.search("(?P<url>https?://[^\s]+)", link)
    if uri_rec:
        print('Url found')
        uri = uri_rec.group("url")
#       print(uri)
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
            return('Something went wrong, let @blood_skull_boi84 know')
        else:
            pass
    else:
        return 'No valid URL found'
    if 'archive.fo' in archive_uri:
#       print(archive_uri)
        return archive_uri
    elif 'archive.is' in archive_uri:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
#                    [InlineKeyboardButton(text='Force save page', callback_data='save')],
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
        return 'Something went wrong, let @blood_skull_boi84 know'

def archive_create(uri):
    url = 'https://archive.fo/submit/'
    values = { 'url': uri, 'anyway': 1, 'submitid': 'Q0LhFSPD/nfL9rXQ8zNiQREHCs80rH2uT9OsQDA+DR4rGJzt77/yS8bM1HZgW9aM' }
    headers = { 'User-Agent' : 'Telegram archive bot - https://github.com/raku-cat/archiveis-tg' }
    r = requests.post(url, values, headers)
    response = r.text
#    print(response)
    archive_uri = response.split('"')[1]
    if 'archive.fo' not in archive_uri:
        print('Archive creation failed')
        return('Something went wrong, let @blood_skull_boi84 know')
    else:
        print('Archive creation sucessful')
        return archive_uri

bot.message_loop({'chat': on_chat_command,
        'inline_query': on_inline_query,
        'edited_chat': on_chat_command,
        'callback_query': on_callback_query,
        },
        run_forever='Started...')
