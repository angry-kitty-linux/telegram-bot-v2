#!/usr/bin/python
# -*- coding: utf8 -*-

from config import bot
import time
from plugins.error import Error
from plugins.error import (in_chat,
                           check_admin,
                           check_private,
                           check_reply,
                           check_exist_user)


@in_chat()
@check_admin()
@check_private()
@check_reply()
@check_exist_user()
def mute(m):
    """ Команда /mute """
    bot.delete_message(m.chat.id, m.message_id)

    check_admin = Error(m, bot).check_reply_admin_()

    if m.reply_to_message.from_user.id == 905933085:
        bot.send_message(m.chat.id,
                         text="*Не трошь её!*",
                         parse_mode="Markdown")
        time.sleep(2)
        bot.delete_message(m.chat.id, m.message_id + 1)
        bot.send_sticker(m.chat.id,
                         "CAACAgIAAxkBAAIalF94SmIocEzaL6j2Yaz4IAM_u"
                         "eoMAAIBAQACnxUvEo9CUplzfDv9GwQ")
        time.sleep(5)
        bot.delete_message(m.chat.id, m.message_id + 2)
##########################################################################
    else:                                      # Если человек не
        if check_admin is False:
            Error(m, bot).message_admin()
        if check_admin is True:
            bot.restrict_chat_member(m.chat.id,
                                     m.reply_to_message.from_user.id,
                                     can_send_messages=False)
            bot.send_message(
                m.chat.id,
                text=f"*{m.reply_to_message.from_user.first_name}* _замолк "
                " на %x минут!_", parse_mode="Markdown")

    # m.from_user.id - айди человека, который хочет замутить
    # m.reply_to_message - проверить, переслано ли сообщение
    # m.reply_to_message.from_user.id - айди человека, которого мутят


@in_chat()
@check_private()
@check_reply()
@check_admin()
@check_exist_user()
def unmute(m):
    """ Команда /unmute """
    bot.delete_message(m.chat.id, m.message_id)
    check_admin = Error(m, bot).check_reply_admin_()

    if check_admin is True:
        umute = "_Вам разрешено отправлять сюда сообщения._ "
        "*Будь хорошим мальчиком!*"
        if m.reply_to_message.from_user.id:
            bot.restrict_chat_member(m.chat.id,
                                     m.reply_to_message.from_user.id,
                                     can_send_messages=True,
                                     can_send_media_messages=True,
                                     can_send_other_messages=True,
                                     can_add_web_page_previews=True)
            bot.send_message(m.chat.id,
                             umute,
                             reply_to_message_id=m.reply_to_message.message_id,
                             parse_mode="Markdown")
        else:
            bot.restrict_chat_member(m.chat.id,
                                     m.reply_to_message.from_user.username,
                                     can_send_messages=True,
                                     can_send_media_messages=True,
                                     can_send_other_messages=True,
                                     can_add_web_page_previews=True)
            bot.send_message(m.chat.id, umute,
                             reply_to_message_id=m.reply_to_message.message_id)
    else:
        delete = bot.send_message(
                        m.chat.id,
                        "Пользователь и так может свободно общаться в чате")
        time.sleep(5)
        bot.delete_message(m.chat.id, delete.message_id)
