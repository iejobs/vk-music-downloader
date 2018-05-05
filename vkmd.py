# -*- coding: utf-8 -*-

import config
import os
import webbrowser
import urllib.request
import string
import json
import threading

from urllib.parse import urlparse
from queue import Queue


token = ''
user_id = ''
dest_folder = config.DEST_FOLDER
q = Queue()


def auth():
    if not os.path.isfile(config.TOKEN_FILE) or os.stat(config.TOKEN_FILE).st_size == 0:
        create_token()
    else:
        get_token()


def create_token():
    global token

    webbrowser.open(config.AUTH_URL)

    url = input("Введите адрес открывшейся страницы: ")
    token = urlparse(url).fragment.split('&')[0]

    f = open(config.TOKEN_FILE, 'w')
    f.write(token)
    f.close()


def get_token():
    global token

    f = open(config.TOKEN_FILE, 'r')
    token = f.read()
    f.close()


def set_user_id():
    global user_id

    print()
    user_id = input('Введите ID пользователя, чьи аудиозаписи надо скачать: ')


def set_dest_folder():
    global dest_folder

    print('\nТекущая папка для музыки: ' + os.getcwd() + os.sep + dest_folder + '\n')

    new_dest_folder = input('Новая: ')
    new_dest_folder_check = input('Еще раз, чтобы точно: ')

    print()

    if new_dest_folder and new_dest_folder_check and new_dest_folder == new_dest_folder_check:
        dest_folder = new_dest_folder

        print('Новая папка для музыки: ' + dest_folder)
        print()


def get_audio():
    global q
    global dest_folder

    while True:
        audio = q.get()

        file_name = audio['artist'].replace('"', '') + ' - ' + audio['title'].replace('"', '')
        file_ext = '.mp3'
        file = dest_folder + file_name + file_ext

        if os.path.isfile(file):
            print(file_name + file_ext + ' уже существует')
        else:
            print('Скачивается ' + file_name)
            urllib.request.urlretrieve(audio['url'], file)

        q.task_done()


def vkapi_query(method, params):
    try:
        query = 'https://api.vk.com/method/' + method + '?'
        for param in params:
            if query[-1:] != '?':
                query += '&'

            if param[0]:
                query += param[0] + '=' + param[1]
            else:
                query += param[1]

        response = urllib.request.urlopen(query)
        data = json.loads(response.read().decode('utf-8'))
        del data['response'][0]

        return data
    except:
        return False


def download(album_id):
    global dest_folder
    global user_id
    global token
    global q

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    if album_id != '0':
        album = '&album_id=' + album_id
    else:
        album = ''

    data = vkapi_query('audio.get', [['owner_id', user_id], ['', album], ['', token]])
    if not data:
        print('Ошибка')
        return

    for audio in data['response']:
        q.put(audio)

    for i in range(config.THREAD_COUNT):
        t = threading.Thread(target=get_audio)
        t.start()

    q.join()


def get_albums():
    global user_id
    global token

    if not user_id:
        set_user_id()

    data = vkapi_query('audio.getAlbums', [['owner_id', user_id], ['', token]])
    if not data:
        print('Ошибка')
        return

    if data.get('response') == None and data['error']['error_code'] == 5:
        choose = input('Что-то не так с access_token, давайте попробуем пересоздать, нажмите Enter. Чтобы выйти введите q: ')

        if choose == 'q':
            print()
            return
        else:
            create_token()
            print()
            menu()
    
    print('\nСписок альбомов пользователя:')

    if len(data) > 0:
        print('\tID\t\tTITLE')

        for album in data['response']:
            print('\t' + str(album['album_id']) + '\t' + album['title'])
    else:
        print('Альбомов нет')

    album_id = input('\nВыберите альбом для скачивания (либо ID альбома, либо 0 для всех песен, либо 2 для выхода): ')
    if album_id == '2':
        return

    download(album_id)


def check_ethernet_connection():
    try:
        urllib.request.urlopen('http://vk.com/')
        return True
    except:
        return False


def menu():
    global dest_folder

    print('Выберите действие:')
    print('\t1. Показать список альбомов')
    print('\t2. Изменить папку для музыки (сейчас: ' + dest_folder + ')')
    print('\t3. Задать ID пользователя')
    print('\t0. Выйти')
    print()

    choose = input('Выбор: ')

    if choose == '1':
        get_albums()
    elif choose == '2':
        set_dest_folder()
    elif choose == '3':
        set_user_id()
    else:
        return

    menu()


def main():
    if not check_ethernet_connection():
        print('Ошибка! Проверьте интернет-соединение')
    else:
        auth()
        menu()


if __name__ == '__main__':
    main()