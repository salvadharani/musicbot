#!/usr/bin/env python3

from __future__ import unicode_literals
import os
import logging

import requests
import youtube_dl
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def search_youtube(text):
    url = 'https://www.youtube.com'

    r = requests.get(url + '/results', params={'search_query': text})
    soup = BeautifulSoup(r.content, 'html.parser')
    for tag in soup.find_all('a', {'rel': 'spf-prefetch'}):
        title, video_url = tag.text, url + tag['href']
        if 'googleads' not in video_url:
            return title, video_url


def download(title, video_url):
    ydl_opts = {
        'outtmpl': '{}.%(ext)s'.format(title),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    return {
        'audio': open('{}.mp3'.format(title), 'rb'),
        'title': title,
    }


def start(bot, update):
    update.message.reply_text("Music Downloader")


def music(bot, update):
    title, video_url = search_youtube(update.message.text)
    music_dict = download(title, video_url)
    update.message.reply_audio(**music_dict)
    os.remove(title + '.mp3')


def main():
    u = Updater('YOUR-TOKEN')
    dp = u.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, music))

    u.start_polling()
    u.idle()

if __name__ == '__main__':
    main()
