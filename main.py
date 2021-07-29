import requests
import sqlite3
import re
import time
from config import *
import feedparser
import colorama

reset = colorama.Fore.RESET
green = colorama.Fore.GREEN
cyan = colorama.Fore.CYAN
magenta = colorama.Fore.MAGENTA
yellow = colorama.Fore.YELLOW

class db:
    
    def __init__(self):
        filename = 'fl.db'
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            create table if not exists projects (
                id integer primary key autoincrement,
                link text
            )
            """
        )
        self.connection.commit()
    
    def link_new(self, link):
        """
        link_new(self, link) - проверка есть ли ссылка на вакансию в базе
        """
        self.cursor.execute(
            f"SELECT * FROM projects WHERE link = '{link}'"
        )
        result = self.cursor.fetchall()
        if len(result) > 0:
            return False
        else:
            return True
    
    def add_link(self, link):
        """
        add_link(self, link) - Добавление ссылки на вакансию в базу
        """
        self.cursor.execute(
            f'INSERT INTO projects (link) VALUES ("{link}")'
        )
        self.connection.commit()

def log(msg):
    print(colorama.Fore.YELLOW, time.ctime(),
          colorama.Fore.WHITE, ' '+str(msg))

def send_tg(msg, chat_id):
    url_parts = [
        f'https://api.telegram.org/bot{bot_token}',
        f'/sendMessage?chat_id={chat_id}&',
        'disable_web_page_preview=true&',
        'parse_mode=html&text=',
        msg
    ]
    result = None
    try:
        result = requests.get(''.join(url_parts))
    except Exception as E:
        log(str(E))
    if result != None and not result.json()['ok']:
        log(str(result.json()))
    

def parse_fl():
    log('=  '*20)
    log('Проверка новых проектов...')
    result = requests.get(f'https://www.fl.ru/rss/all.xml?category={category}')
    parsed = feedparser.parse(result.text)
    log(f'Всего получено {cyan}{len(parsed["entries"])}{reset} проеков')
    for project in parsed['entries']:
        
        title = project['title']
        if 'Бюджет' in title:
            money = re.search('\(\D*(\d+)',title).group(1)
            title = re.search('(.*)\(Б', title).group(1)
        else:
            money = 0
        text = project['summary_detail']['value']
        link = project['link']
        
        success = False
        for kw in keywords:
            if (
                kw in title.lower() or
                kw in text.lower()
            ):
                success = True

        if success:
            msg = f"<a href='{link}'>{title}</a>\n<b>Бюджет: {money}</b>\n<i>{text}</i>"
            if DB.link_new(link):
                log(
                    f'{magenta}Новый проект:{reset} {title} ({green}Бюджет: {money}{reset})'
                )
                send_tg(msg,chat_id)
                DB.add_link(link)

DB = db()

while True:
    parse_fl()
    time.sleep(60*5)
