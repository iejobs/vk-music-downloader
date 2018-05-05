# -*- coding: utf-8 -*-

import os


# id приложения vk.com
APP_ID = '000'

# файл, в котором будет храниться access_token
TOKEN_FILE = 'token'

# ссылка для авторизация, открывается в браузере по умолчанию
AUTH_URL = 'https://oauth.vk.com/authorize?client_id=' + APP_ID + 'groups_id=1&display=page&redirect_uri=&scope=audio&response_type=token&v=5.53'

# папка, куда будет скачиваться музыка
DEST_FOLDER = os.getcwd() + os.sep + 'music' + os.sep

# количество потоков для скачивания
THREAD_COUNT = 4