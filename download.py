from __future__ import unicode_literals
import youtube_dl
import os
import telebot
import re
import time

TOKEN = os.environ["TOKEN"]
bot = telebot.TeleBot(TOKEN)


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def import_video(link):
    def my_hook(d):
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'max_filesize': 52428800,
        'restrictfilenames': True,
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': False,
        'progress_hooks': [my_hook],
        'forceduration': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        file_name = ydl.prepare_filename(info_dict)
        print('\n' + file_name + '\n')
        if info_dict['duration'] < 1500:
            ydl.download([link])
        else:
            return
    return file_name


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 f'Ну привет, {message.from_user.first_name}. \nКидай мне ссылки youtube на песни, я их верну в mp3')


@bot.message_handler(func=lambda m: True, content_types=['text'])
def send_welcome(message):
    print(message.from_user.first_name)
    link = message.text
    print(link)
    if not (re.match(r'^[A-Za-z0-9_-]{11}$', link.split('/')[-1]) or re.match(r'^[A-Za-z0-9_-]{11}$',
                                                                              link.split('?v=')[-1])):
        bot.reply_to(message, 'И что мне с этим делать?')
        return
    bot.send_message(message.chat.id, 'Запрос обрабатывается')
    file_name = import_video(link)
    print(file_name)
    if not file_name:
        print('work')
        bot.send_message(message.chat.id, 'Слишком длинное видео')
        return
    file_name = file_name.split('.')
    file_name[-1] = 'mp3'
    file_name = '.'.join(file_name)
    audio = open(file_name, 'rb')
    bot.send_audio(message.chat.id, audio)
    os.remove(file_name)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            print(e)
