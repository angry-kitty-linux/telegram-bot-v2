#!/usr/bin/python
# -*- coding: utf8 -*-

""" Взаимодействие с кнопками """

import random
import os
import datetime

from time import sleep
from itertools import islice
import requests

from telebot import apihelper
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as bs
import pickle

from config import bot, conn
from plugins.get import urls_citata
from plugins.log_error import logfile
from plugins.arch_news import send_callback_news
from plugins.arch_news import arch__news
from config import HEADERS
from telebot import types

from plugins.roll import edit_message_callback
from plugins.roll import roll
from plugins.roll import roll_function
from plugins.crocodile import crocodile
from plugins.crocodile import new_crocodile
# 58 строка


# _________________________________________________________

def callback_inline(call):
    """ Если сообщение из чата с ботом """
    if call.message:
        ##################################################################
        # Игра-крокодил
        if call.data == "word":
            if str(crocodile.__annotations__["who_start"]
                   ) in str(call.from_user.id):
                word_txt = crocodile.__annotations__['word_txt']
                bot.answer_callback_query(callback_query_id=call.id,
                                          text=f'Ваше слово: {word_txt}')
            else:
                bot.answer_callback_query(call.id, text="Вы не ведущий!")

        if call.data.startswith("new_word"):
            id_user = call.data.split("&&")[1]
            if str(id_user) in str(call.from_user.id):
                line = random.randint(1, 125853)
                with open('plugins/singular_and_plural.txt') as file:
                    word_txt = next(islice(file, line, None))
                crocodile.__annotations__['word_txt'] = word_txt
                bot.answer_callback_query(call.id,
                                          text=f"Ваше слово: {word_txt}")
            else:
                bot.answer_callback_query(call.id, text="Вы не ведущий!")

        if call.data.startswith("new_crocodile"):
            new_crocodile(call)

        ########################################
        if call.data.endswith("roll"):
            first_name = call.from_user.first_name
            from plugins.roll import text_info_user  # Да простит меня PEP

        # Обработка ЧЕРНОГО 'ролла' при условии,
        # что человек не нажимал кнопку

        if (call.data.startswith("black_roll")
                and first_name not in text_info_user["names"]):
            text_info_user["names"].append(first_name)
            text_info_user["colors"].append("⚫")
        #########

        # Обработка КРАСНОГО 'ролла' при условии,
        # что человек не нажимал кнопку
        if (call.data.startswith("red_roll")
                and first_name not in text_info_user["names"]):
            text_info_user["names"].append(first_name)
            text_info_user["colors"].append("🔴")
            edit_message_callback(call)
        #########

        # Обработка ЗЕЛЕНОГО 'ролла' при условии,
        # что человек не нажимал кнопку
        if (call.data.startswith("green_roll")
                and first_name not in text_info_user["names"]):
            text_info_user["names"].append(first_name)
            text_info_user["colors"].append("🟢")
            edit_message_callback(call)

        # Обработка кнопки "Крутить"
        if call.data == "roll_fast":
            # Кнопки для удаления сообщения
            keyboard_delete_last = types.InlineKeyboardMarkup()
            keyboard_delete = types.InlineKeyboardButton(text="❌",
                                                         callback_data="delete"
                                                         )
            keyboard_delete_last.add(keyboard_delete)
            #########
            roll.__annotations__["fast_roll"] = True
            roll_winner = roll_function()

            if roll_winner is None:
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="_Увы, никто не выиграл!_",
                                      parse_mode="Markdown",
                                      reply_markup=keyboard_delete_last)

            else:
                winners_enum, win_color = roll_winner
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=f" _Выпало_ *{win_color}*"
                                           "_Победители:_"
                                           f"\n\n {winners_enum}",
                                      parse_mode="Markdown",
                                      reply_markup=keyboard_delete_last)
    ########################################

        if call.data == "delete_full":
            if call.from_user.id == id_user:
                bot.delete_message(call.message.chat.id,
                                   call.message.message_id)

                bot.delete_message(call.message.chat.id,
                                   call.message.message_id + 1)

        elif call.data == "next" or call.data == "back":
            keyboard = types.InlineKeyboardMarkup()
            keyboard_delete_ = types.InlineKeyboardMarkup()

            keyboard_delete = types.InlineKeyboardButton(text="❌",
                                                         callback_data="delete"
                                                                       "_news")
            keyboard_one = types.InlineKeyboardButton(text="1⃣",
                                                      callback_data="b_zero")
            keyboard_two = types.InlineKeyboardButton(text="2⃣",
                                                      callback_data="b_one")
            keyboard_tree = types.InlineKeyboardButton(text="3⃣",
                                                       callback_data="b_two")
            keyboard_next = types.InlineKeyboardButton(text="🔜",
                                                       callback_data="next")

            keyboard_delete_.add(keyboard_delete)

            res = requests.get("https://archlinux.org.ru/news/",
                               headers=HEADERS)
            html = bs(res.text, "lxml")
            find = html.find_all("div", {"class": "block"})

            with open("plugins/.arch_news_info.pickle", "rb") as file:
                download = pickle.load(file)

            links = download["links"]
            titles = download["titles"]

            full_links = ["https://archlinux.org.ru" + line
                          for line in links]

            titles_3 = titles[:3]
            full_links_3 = full_links[:3]
            full = []

            number = len(titles_3)

            if number == 3:
                keyboard.add(keyboard_one,
                             keyboard_two,
                             keyboard_tree,
                             keyboard_delete,
                             keyboard_next)

                for line in range(3):  # Превращаем обычный текст в ссыль
                    full.append(f"[{0}]({1})".format(titles_3[line],
                                                     full_links_3[line]))
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="\n\n".join(full),
                                      reply_markup=keyboard,
                                      parse_mode="Markdown")
            elif number == 2:
                keyboard.add(keyboard_one,
                             keyboard_two,
                             keyboard_delete,
                             keyboard_next)

                for line in range(2):  # Превращаем обычный текст в ссыль
                    full.append("[{0}]({1})".format(titles_3[line],
                                                    full_links_3[line]))

                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="\n\n".join(full),
                                      reply_markup=keyboard,
                                      parse_mode="Markdown")

            elif number == 0:
                full = ("*😫😫 Новоcти кончились 😫😫*")
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=full,
                                      reply_markup=keyboard_delete_,
                                      parse_mode="Markdown")
                os.system("cat /dev/null > plugins/.arch_news_info.pickle")

            del links[:3]       # "Перелистываем"
            del titles[:3]

            with open("plugins/.arch_news_info.pickle", "wb") as file:
                pickle.dump({
                    "titles": titles,
                    "links": links
                }, file)

            titles = titles[3:]
            full_links = full_links[3:]

        elif call.data == "b_zero":  # Кнопки
            send_callback_news(call, 0)

        elif call.data == "b_one":
            send_callback_news(call, 1)

        elif call.data == "b_two":
            send_callback_news(call, 2)

#  ___________________________________________________________________________
#  Самые главные кнопки, где книги и прочее
#  ___________________________________________________________________________
        if call.data == "book":
            bot.send_chat_action(call.message.chat.id, 'typing')
            keyb = types.InlineKeyboardMarkup()
            books = types.InlineKeyboardButton(text="Книги📚",
                                               callback_data="books")
            video = types.InlineKeyboardButton(text="Видеокурсы📹",
                                               callback_data="video")
            vkus = types.InlineKeyboardButton(text="Вкусняшки😋",
                                              callback_data="vkus")
            service = types.InlineKeyboardButton(text="Сервисы😧",
                                                 callback_data="servise")
            slovar = types.InlineKeyboardButton(text="Словари брут📖",
                                                callback_data="slovar")
            audio = types.InlineKeyboardButton(text="Аудиокниги🔊",
                                               callback_data="audio")
            back = types.InlineKeyboardButton(text="🔙",
                                              callback_data="glav")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            keyb.add(books, video, vkus,
                     service, slovar, audio)
            keyb.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*Какой пункт выберешь?*",
                                  reply_markup=keyb,
                                  parse_mode="Markdown")
        elif call.data == "infa":
            bot.send_chat_action(call.message.chat.id, 'typing')
            key = types.InlineKeyboardMarkup()
            arch = types.InlineKeyboardButton("Arch Linux",
                                              callback_data="arch linux")
            ubuntu = types.InlineKeyboardButton("Ubuntu Linux",
                                                callback_data="ubuntu "
                                                              "linux")
            debian = types.InlineKeyboardButton("Debian Linux",
                                                callback_data="debian "
                                                              "linux")
            gentoo = types.InlineKeyboardButton("Gentoo Linux",
                                                callback_data="gentoo "
                                                              "linux")
            lfs = types.InlineKeyboardButton("LFS",
                                             callback_data="lfs linux")
            kali = types.InlineKeyboardButton("Kali Linux",
                                              callback_data="kali linux")
            back = types.InlineKeyboardButton("🔙", callback_data="glav")
            delete = types.InlineKeyboardButton("❌",
                                                callback_data="delete")
            key.add(arch, ubuntu, debian, gentoo, lfs, kali)
            key.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*Какой дистрибутив желаешь?*",
                                  reply_markup=key,
                                  parse_mode="Markdown")
        elif call.data == "glav":
            bot.send_chat_action(call.message.chat.id, 'typing')
            keyboard = types.InlineKeyboardMarkup()
            book = types.InlineKeyboardButton(text="Обучаться📚",
                                              callback_data="book")

            infa = types.InlineKeyboardButton(text="Wiki Linux",
                                              callback_data="infa")

            citata = types.InlineKeyboardButton(text="Цитата🤤",
                                                callback_data="citata")

            commands_help = types.InlineKeyboardButton(
                                                text="Помощь по командам📄",
                                                callback_data="helpmenu")

            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            keyboard.add(book, infa, citata, commands_help)
            keyboard.add(delete)

            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*Что желаешь?*",
                                  reply_markup=keyboard,
                                  parse_mode="Markdown")

        elif call.data == "books":
            markup = types.InlineKeyboardMarkup()
            btn_site = types.InlineKeyboardButton('🔜',
                                                  'https://clck.ru/N3e6i')

            back = types.InlineKeyboardButton(text="🔙",
                                              callback_data="book")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(btn_site)
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*Книги, читаем и развиваемся*📚",
                                  reply_markup=markup,
                                  parse_mode="Markdown")

        elif call.data == "video":
            markup = types.InlineKeyboardMarkup()
            btn_site = types.InlineKeyboardButton('🔜',
                                                  'https://clck.ru/N3eBX')
            back = types.InlineKeyboardButton(text="🔙",
                                              callback_data="book")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(btn_site)
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*Видеокурсы*📹",
                                  reply_markup=markup,
                                  parse_mode="Markdown")

        elif call.data == "vkus":
            markup = types.InlineKeyboardMarkup()
            btn_site = types.InlineKeyboardButton(text='🔜',
                                                  url='https://clck.ru/MoUC7')
            back = types.InlineKeyboardButton(text="🔙",
                                              callback_data="book")

            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(btn_site)
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*Вкусняшки*😋",
                                  reply_markup=markup,
                                  parse_mode="Markdown")

        elif call.data == "servise":
            markup = types.InlineKeyboardMarkup()
            btn_site = types.InlineKeyboardButton(text='🔜',
                                                  url='https://clck.ru/NBvQt')

            back = types.InlineKeyboardButton(text="🔙",
                                              callback_data="book")

            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(btn_site)
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*Сервисы*😧",
                                  reply_markup=markup,
                                  parse_mode="Markdown")

        elif call.data == "slovar":
            markup = types.InlineKeyboardMarkup()
            btn_site = types.InlineKeyboardButton(text='🔜',
                                                  url='https://clck.ru/NPLf6')
            back = types.InlineKeyboardButton(text="🔙",
                                              callback_data="book")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(btn_site)
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*Словари для брутфорса*📖",
                                  reply_markup=markup,
                                  parse_mode="Markdown")

        elif call.data == "audio":
            markup = types.InlineKeyboardMarkup()
            btn_my_site = types.InlineKeyboardButton(text='🔜',
                                                     url='https://clck.ru'
                                                     '/MpokB')

            back = types.InlineKeyboardButton(text="🔙",
                                              callback_data="book")

            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(btn_my_site)
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*Аудиокурсы*🔊",
                                  reply_markup=markup,
                                  parse_mode="Markdown")
    #  __________________________________________________________________________
    #  Рандомные цитатики
    #  __________________________________________________________________________
        elif call.data == "citata":
            try:
                markup = types.InlineKeyboardMarkup()
                duble = types.InlineKeyboardButton(text="Еще цитату😋",
                                                   callback_data="citata")

                back = types.InlineKeyboardButton(text="🔙",
                                                  callback_data="glav")

                delete = types.InlineKeyboardButton(text="❌",
                                                    callback_data="delete"
                                                    )
                markup.add(duble)
                markup.add(back, delete)
                url = urls_citata()

                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=url,
                                      reply_markup=markup)
            except apihelper.ApiTelegramException:
                logfile(call, "Злоупотребление кнопками").time()
    # __________________________________________________________________________
    # Кнопки для wiki and download linux
    # __________________________________________________________________________

        elif call.data == "arch linux":
            markup = types.InlineKeyboardMarkup()
            downloads = types.InlineKeyboardButton(text='Загрузить',
                                                   url='archlinux.org/download'
                                                   )
            wiki = types.InlineKeyboardButton(text='Вики',
                                              url='wiki.archlinux.org')

            install = types.InlineKeyboardButton(text='Инструкция',
                                                 url='https://clck.ru/N5eWx'
                                                 )
            back = types.InlineKeyboardButton(text="🔙", callback_data="infa")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(downloads, wiki, install)
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*[Arch Linux]  Для самых привер"
                                       "едливых*",
                                  reply_markup=markup, parse_mode="Markdown")
        elif call.data == "ubuntu linux":
            markup = types.InlineKeyboardMarkup()
            downloads = types.InlineKeyboardButton(text='Загрузить',
                                                   url='releases.ubuntu.com')
            wiki = types.InlineKeyboardButton(text='Вики',
                                              url='help.ubuntu.ru/wiki/'
                                                  'главная')
            back = types.InlineKeyboardButton(text="🔙", callback_data="infa")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(downloads, wiki)
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*[Ubuntu Linux]   Для самых маленьких"
                                       "котят*",
                                  reply_markup=markup,
                                  parse_mode="Markdown")

        elif call.data == "debian linux":
            markup = types.InlineKeyboardMarkup()
            downloads = types.InlineKeyboardButton(text='Загрузить',
                                                   url='debian.org/CD/')
            wiki = types.InlineKeyboardButton(text='Вики',
                                              url='wiki.debian.org/ru/'
                                                  'DebianRussian')
            back = types.InlineKeyboardButton(text="🔙", callback_data="infa")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(downloads, wiki)
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*[Debian Linux]   Для любителей "
                                       "серверов*",
                                  reply_markup=markup,
                                  parse_mode="Markdown")

        elif call.data == "gentoo linux":
            markup = types.InlineKeyboardMarkup()
            downloads = types.InlineKeyboardButton(text='Загрузить',
                                                   url='gentoo.org/downloads')
            wiki = types.InlineKeyboardButton(text='Handbook',
                                              url='wiki.gentoo.org/wiki/'
                                              'Handbook:Main_Pagecg/ru')
            back = types.InlineKeyboardButton(text="🔙", callback_data="infa")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(downloads, wiki)
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*[Gentoo Linux]   Для вегетарианцев*",
                                  reply_markup=markup,
                                  parse_mode="Markdown")
        elif call.data == "lfs linux":
            markup = types.InlineKeyboardMarkup()
            downloads = types.InlineKeyboardButton(text='Загрузить',
                                                   url='linuxfromscratch.org')
            wiki = types.InlineKeyboardButton(text='Russian book',
                                              url='book.linuxfromscratch.ru')
            back = types.InlineKeyboardButton(text="🔙", callback_data="infa")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(downloads, wiki)
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*[LFS Linux]  "
                                  "Тут даже нечего сказать*",
                                  reply_markup=markup,
                                  parse_mode="Markdown")

        elif call.data == "kali linux":
            markup = types.InlineKeyboardMarkup()
            btn_site = types.InlineKeyboardButton(text='Взломать',
                                                  url='https://clck.ru/JwL3')
            back = types.InlineKeyboardButton(text="🔙", callback_data="infa")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(btn_site)
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*[Kall Linux]   Наше время пришло,"
                                  " мой друг*",
                                  reply_markup=markup,
                                  parse_mode="Markdown")
    #  ________________________________________________________________________
    #  Кнопки для команды /help
    #  ________________________________________________________________________
        elif call.data == "helpmenu":
            keyboard = types.InlineKeyboardMarkup()  # Добавляем кнопки
            commands_user = types.InlineKeyboardButton("Пользователь🤵",
                                                       callback_data="user")

            commands_admin = types.InlineKeyboardButton("Админ🤴",
                                                        callback_data="admins")
            back = types.InlineKeyboardButton(text="🔙",
                                              callback_data="glav")

            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")

            keyboard.add(commands_user, commands_admin)
            # Добавляем кнопки для вывода
            keyboard.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="*Кто ты?*",
                                  reply_markup=keyboard,
                                  parse_mode="Markdown")
            #  Выводим кнопки и сообщение
        elif call.data == "user":
            markup = types.InlineKeyboardMarkup()
            back = types.InlineKeyboardButton(text="🔙",
                                              callback_data="helpmenu")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(back, delete)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="📎*Команды для пользователя*📎"
                                       "\n`/start` - _запустить бота_"
                                       "\n`/id` - _Узнать свой Telegram ID_"
                                       "\n`/github` - _Репозиторий кота_"
                                       "\n`/say` *text* - _крик из толпы_"
                                       "\n`/invite` - _Получить "
                                       "пригласительную ссылку_"
                                       "\n`/cats` - _Получить рандомных "
                                       "котеек_"
                                       "\n`/encode` *text* - _Закодировать "
                                       "в base64_"
                                       "\n`/ping` - _Проверить работоспособн"
                                       "ость бота_"
                                       "\n`/decode` *text* - _Декодировать"
                                       " base64_"
                                       "\n`/url` *Ссылка на сайт* - "
                                       "_Скриншот сайта_"
                                       "\n`/wiki` *text* - _Поиск информации"
                                       " в вики_"
                                       "\n`/ru` *text* - _Перевести на "
                                       "русский_"
                                       "\n`/en` *text* - _Перевести на "
                                       "английский_"
                                       "\n`/post` *text* - _Запостить "
                                       "шутку на канал_"
                                       "\n`/game` - _Игра камень, ножницы, "
                                       "бумага_"
                                       "\n`/crocodile` - _Игра-крокодил_"
                                       "\n`/roll` - _Сыграть в рулетку_"
                                       "\n`/search` *text* - _Поиск в гугле_"
                                       "\n`/sy` *text* - _Поиск в ютубе_"
                                       "\n`/proxy` - _Получить свежий "
                                       "список прокси_"
                                       "\n`/top` - _Показать активных "
                                       "пользователей_"
                                       "\n`/arch_news` - _Показать новости "
                                       "Арча_"
                                       "\n`/news` - _Новости_"
                                       "\n`/whois` *IP* - _Узнать информацию "
                                       "об IP_"
                                       "\n`/kernel` - _Показать последние "
                                       "версии ядер_",
                                       reply_markup=markup,
                                       parse_mode="Markdown")
            #  Выводим кнопки и сообщение parse_mode= "Markdown"
        elif call.data == "admins":
            markup = types.InlineKeyboardMarkup()
            back = types.InlineKeyboardButton(text="🔙",
                                              callback_data="helpmenu")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            markup.add(back, delete)

            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="📎*Команды для админов*📎"
                                  "\n`/kick` - _Кикнуть пользователя_"
                                  "\n`/pin` - _Закрепить пересланное "
                                  "сообщение_"
                                  "\n`/unpin` - _Открепить сообщение_"
                                  "\n`/mute` - _Дать мут дурачку_"
                                  "\n`/unmute` - _Снять мут_"
                                  "\n`/link` - _Получить пригласительную ссылк"
                                  "у, после каждого запроса ссылка меняется_"
                                  "\n`/des`  - _Изменить описание чата, если п"
                                  "устая команда, то описание стирается_ "
                                  "\n`/logs` - _Просмотр журнала ошибок_"
                                  "\n`/unban` *ID* или *Пересланное сообщение*"
                                  " - _Убрать пользователя из черного списка_"
                                  "\n`/restart` - _Перезапустить основного "
                                  "бота_",
                                  reply_markup=markup,
                                  parse_mode="Markdown")
    #  ________________________________________________________________________
    #  Рандомные котейки
    #  ________________________________________________________________________
        elif call.data == "cats":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            keyboard = types.InlineKeyboardMarkup()
            cats = types.InlineKeyboardButton(text="Еще хочу котейку",
                                              callback_data="cats")
            delete = types.InlineKeyboardButton(text="❌",
                                                callback_data="delete")
            keyboard.add(cats, delete)

            search = "https://theoldreader.com/kittens/1366/768/js"
            url = requests.get(search, headers=HEADERS)  # Делаем запрос
            soup = BeautifulSoup(url.text, features="lxml")  # Получаем запрос
            result = soup.find("img").get("src")  # Ищем тег <img src="*.png"
            result = "https://theoldreader.com" + result
            bot.send_photo(chat_id=call.message.chat.id,
                           photo=result,
                           reply_markup=keyboard)
    # _________________________________________________________________________
    # Игра камень ножницы бумага
    # _________________________________________________________________________
        elif call.data == "kamen":
            a = ['Камень', 'Ножницы', 'Бумага']
            comp_number = random.choice(a)
            enter_all = f"_Вы выбрали_ *Камень*_, а мой выбор_ *{comp_number}*"
            if comp_number == "Камень":  # Условие для ничьей
                id_user = call.message.message_id
                delete = bot.edit_message_text(chat_id=call.message.chat.id,
                                               message_id=id_user,
                                               text=f"{enter_all} \n*Ничья*",
                                               parse_mode="Markdown")
                sleep(5)
                bot.delete_message(call.message.chat.id, delete.message_id)
            else:  # Условие для выигрыша или проигрыша
                if comp_number == "Ножницы":
                    txt = "Ты победил, камень поломал ножницы!"
                    message_id = call.message.message_id
                    delete = bot.edit_message_text(
                                                chat_id=call.message.chat.id,
                                                message_id=message_id,
                                                text=f"{enter_all}\n_{txt}_",
                                                parse_mode="Markdown")
                    sleep(5)
                    bot.delete_message(call.message.chat.id, delete.message_id)
                elif comp_number == "Бумага":
                    txt = "Я победил, бумага закатала камень!"
                    delete = bot.edit_message_text(
                                            chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            text=f"{enter_all}"
                                                 "\n_{txt}_",
                                            parse_mode="Markdown")
                    sleep(5)
                    bot.delete_message(call.message.chat.id, delete.message_id)

        elif call.data == "noj":
            a = ['Камень', 'Ножницы', 'Бумага']
            comp_number = random.choice(a)
            enter_all = (f"_Вы выбрали_ *Ножницы*_, "
                         f"а мой выбор_ *{comp_number}*")
            if comp_number == "Ножницы":  # Условие для ничьей
                delete = bot.edit_message_text(
                                            chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            text=f"{enter_all}\n*Ничья*",
                                            parse_mode="Markdown")
                sleep(5)
                bot.delete_message(call.message.chat.id, delete.message_id)
            else:  # Условие для выигрыша или проигрыша
                if comp_number == "Камень":
                    delete = bot.edit_message_text(
                                            chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            text=f"{enter_all}\n_Я победил, "
                                                 "так как вы выбрали ножницы._"
                                                 "*Камень* _поломал ножницы!_",
                                            parse_mode="Markdown")
                    sleep(5)
                    bot.delete_message(call.message.chat.id, delete.message_id)
                elif comp_number == "Бумага":
                    delete = bot.edit_message_text(
                                            chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            text=f"{enter_all}\n_Ты победил, "
                                                 "ножницы разрезали бумагу!_",
                                            parse_mode="Markdown")
                    sleep(5)
                    bot.delete_message(call.message.chat.id, delete.message_id)
        elif call.data == "bumaga":
            a = ['Камень', 'Ножницы', 'Бумага']
            comp_number = random.choice(a)
            enter_all = f"_Вы выбрали_ *Бумага*_, а мой выбор_ *{comp_number}*"
            if comp_number == "Бумага":  # Условие для ничьей
                delete = bot.edit_message_text(
                                            chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            text=f"{enter_all}\n*Ничья*",
                                            parse_mode="Markdown")
                sleep(5)
                bot.delete_message(call.message.chat.id, delete.message_id)
            else:  # Условие для выигрыша или проигрыша
                if comp_number == "Камень":
                    delete = bot.edit_message_text(
                                            chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            text=f"{enter_all}\n_Ты победил(a)"
                                            ", бумага закатала камень!_",
                                            parse_mode="Markdown")
                    sleep(5)
                    bot.delete_message(call.message.chat.id, delete.message_id)
                elif comp_number == "Ножницы":
                    delete = bot.edit_message_text(
                                            chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            text=f"{enter_all}\n_Я победил, "
                                            "ножницы разрезали бумагу!_",
                                            parse_mode="Markdown")
                    sleep(5)
                    bot.delete_message(call.message.chat.id, delete.message_id)
        elif call.data == "delete":
            bot.delete_message(call.message.chat.id, call.message.message_id)
        elif call.data == "delete_news":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            os.system("cat /dev/null > plugins/.arch_news_info.pickle")
        elif call.data == "delete_2":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.delete_message(call.message.chat.id,
                               call.message.message_id - 1)
        elif call.data == "dalee_top":
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT row_number() OVER"
                               "(ORDER BY message::int DESC),"
                               "user_id, name, message, new FROM top_users"
                               )
                rows = cursor.fetchall()
                result_list = []
                del rows[:10]

                for row in rows[:10]:
                    number = row[0]
                    last_name = row[2]
                    message = row[3]
                    result = (f'{number} ✅ {last_name} ✉ = {message}'
                              '\n➖➖➖➖➖➖➖➖➖➖➖➖➖➖')
                    result_list.append(result)
                results_lists_last = "\n".join(result_list)
                markup = types.InlineKeyboardMarkup()
                back_top = types.InlineKeyboardButton(text='🔙',
                                                      callback_data="back_top")
                dalee_top_one = types.InlineKeyboardButton(
                                                text='🔜',
                                                callback_data="dalee_top_one")
                delete = types.InlineKeyboardButton(text="❌",
                                                    callback_data="delete_2")
                markup.add(back_top, dalee_top_one)
                markup.add(delete)  # Отвечаем, если выхов был из супер чата
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="📎Активность пользователей в ч"
                                      "ате📎\n➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖"
                                      f"➖\n{results_lists_last}",
                                      reply_markup=markup)
            except Exception as e:
                print(e)
                markup = types.InlineKeyboardMarkup()
                dalee_top = types.InlineKeyboardButton(
                                                    text='🔙',
                                                    callback_data="dalee_top")
                delete = types.InlineKeyboardButton(text="❌",
                                                    callback_data="delete_2")
                markup.add(dalee_top, delete)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="Таблица пустая, нечего выводить",
                                      reply_markup=markup)
        elif call.data == "back_top":
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT row_number() OVER(ORDER BY message::"
                               "int DESC), user_id, name, message, new, "
                               "date_add FROM top_users;")
                rows = cursor.fetchall()
                result_list = []

                for row in rows[:10]:
                    beginner = ""
                    if row[4] is True:
                        beginner = "[Новичок]"
                        date = row[5].split()

                        year = int(date[0])     # Год
                        month = int(date[1])    # Месяц
                        day = int(date[2])     # День

                        date_new = datetime.date(year, month, day)
                        date_last = datetime.datetime.now().day - date_new.day
                        if date_last >= 5:
                            cursor.execute("UPDATE top_users SET new = "
                                           f"FALSE WHERE user_id = {row[1]};")
                            cursor.execute("UPDATE top_users "
                                           "SET date_add = ''"
                                           "WHERE user_id = {row[1]};")
                            conn.commit()

                    number = row[0]
                    last_name = row[2]
                    message = row[3]
                    result = (f'{number} ✅ {last_name} ✉ = {message}     '
                              f'{beginner}\n➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖'
                              )
                    result_list.append(result)

                results_lists_last = "\n".join(result_list)
                markup = types.InlineKeyboardMarkup()
                dalee_top = types.InlineKeyboardButton(
                                                    text='🔜',
                                                    callback_data="dalee_top")
                delete = types.InlineKeyboardButton(text="❌",
                                                    callback_data="delete_2")
                markup.add(dalee_top, delete)
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="📎Активность пользователей в чате"
                    "📎\n➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖"
                    f"➖➖\n{results_lists_last}",
                    reply_markup=markup)
            except Exception as e:
                print(e)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="Таблица пустая, нечего выводить")
        elif call.data == "dalee_top_one":
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT row_number()"
                               "OVER(ORDER BY message::int DESC)"
                               ", user_id, name, message, new, date_add"
                               "FROM top_users;")
                rows = cursor.fetchall()
                result_list = []

                beginner = ""
                for row in rows[20:30]:
                    if row[4] is True:
                        beginner = "[Новичок]"
                        date = row[5].split()

                        year = int(date[0])     # Год
                        month = int(date[1])    # Месяц
                        day = int(date[2])     # День

                        date_new = datetime.date(year, month, day)
                        date_last = datetime.datetime.now().day - date_new.day
                        if date_last >= 5:
                            cursor.execute("UPDATE top_users SET new = FALSE"
                                           f"WHERE user_id = {row[1]};")
                            cursor.execute("UPDATE top_users"
                                           "SET date_add = ''"
                                           f"WHERE user_id = {row[1]};")
                            conn.commit()
                    number = row[0]
                    last_name = row[2]
                    message = row[3]
                    result = f'{number} ✅ {last_name} ✉ = '
                    '{message}    {beginner}\n➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖'
                    result_list.append(result)
                results_lists_last = "\n".join(result_list)

                markup = types.InlineKeyboardMarkup()
                dalee_top = types.InlineKeyboardButton(
                                                    text='🔙',
                                                    callback_data="dalee_top")

                delete = types.InlineKeyboardButton(text="❌",
                                                    callback_data="delete_2")
                markup.add(dalee_top, delete)
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="📎Активность пользователей в чате"
                    "📎\n➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖"
                    f"➖\n{results_lists_last}",
                    reply_markup=markup)
            except Exception as e:
                print(e)
                markup = types.InlineKeyboardMarkup()
                dalee_top = types.InlineKeyboardButton(
                                                    text='🔙',
                                                    callback_data="dalee_top")
                delete = types.InlineKeyboardButton(
                                                text="❌",
                                                callback_data="delete_2")
                markup.add(dalee_top, delete)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="Таблица пустая, нечего выводить",
                                      reply_markup=markup)
