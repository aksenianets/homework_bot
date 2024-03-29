import random
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import handlers.funcs
import handlers.log
import handlers.env

NEXT = ""
VALID_HASHTAGS = handlers.env.ValHash.VALIDHASHTAGS


async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save user's homework message."""

    if not update.edited_message:
        chat = update.message.chat
        chat_id = chat.id
        chat_title = chat.title
        username = update.message.from_user.username
    else:
        chat = update.edited_message.chat
        chat_id = chat.id
        chat_title = chat.title
        username = update.edited_message.from_user.username

    # Check if the chat is already registered
    chats = [x[0] for x in handlers.funcs.get_chats()]
    if chat_id not in chats:
        handlers.funcs.add_chat(chat_id, chat_title)

    # Process caption and entities
    hashtag_text = None
    if not update.edited_message:
        mess_capt_entities = update.message.caption_entities
        mess_entities = update.message.entities
    else:
        mess_capt_entities = update.edited_message.caption_entities
        mess_entities = update.edited_message.entities

    # проверка есть ли хэштег
    if mess_capt_entities or mess_entities:
        if mess_capt_entities:
            # если есть фотка
            if not update.edited_message:
                hashtag_text = update.message.parse_caption_entity(
                    mess_capt_entities[0]
                )
            else:
                hashtag_text = update.edited_message.parse_caption_entity(
                    mess_capt_entities[0]
                )
        else:
            # если её нет
            if not update.edited_message:
                hashtag_text = update.message.parse_entity(mess_entities[0])
            else:
                hashtag_text = update.edited_message.parse_entity(mess_entities[0])

    if hashtag_text:
        # Check if the hashtag is valid
        if hashtag_text in VALID_HASHTAGS.keys():
            if not update.edited_message:
                handlers.funcs.add_homework(chat_id, hashtag_text, update.message.id)
            else:
                handlers.funcs.add_homework(
                    chat_id, hashtag_text, update.edited_message.id
                )

            # Log the saved homework
            handlers.log.logger.info(
                "Saved %s from %s in %s",
                hashtag_text,
                username,
                chat_title,
            )

            if not update.edited_message:
                await update.message.reply_text(
                    random.choice(
                        [
                            "Я это запомню...",
                            "Мдаа, зачем это делать..",
                            "Ну устно, так устно))",
                            "Пон.",
                            "Меняй!",
                            "No comments",
                            "Предлагаю не делать)",
                            "Делайте тг-ботов, а не вот это вот всё",
                            "Не придумал, что ответить",
                            "Сомнительноо, но окэй...",
                            "Вот мне лично это не интересно, за других сказать не могу",
                            "Соболезную, ребят...",
                            "Что-то в этом есть, но может ну его?..",
                            "Не в моих интересах.",
                        ]
                    )
                )
            else:
                await update.edited_message.reply_text(
                    random.choice(
                        [
                            "Ладно, раз изменил, то запомню ещё разок",
                            "Я то запомню, а ты??",
                            "СМОТРИТЕ ВСЕ! ОН ИЗМЕНИЛ СООБЩЕНИЕ!!",
                            "Ну и что поменялось? :|",
                            "Ну началось! Я только запомнил, а ты уже правишь...",
                            "Да сколько можно править, я же не машина для запоминания!",
                        ]
                    )
                )

            return NEXT

    # Save the last homework if no new homework is provided
    last_homework = handlers.funcs.get_last_homework(chat_id)
    if last_homework:
        if not update.edited_message:
            handlers.funcs.add_homework(chat_id, last_homework, update.message.id)
        else:
            handlers.funcs.add_homework(
                chat_id, last_homework, update.edited_message.id
            )

    return ConversationHandler.END


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


# by aksenianets
