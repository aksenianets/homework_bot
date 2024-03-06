# from telegram import Update
# from telegram.ext import ContextTypes, ConversationHandler


# from handlers import funcs, log, env

# NEXT = ""
# VALIDHASHTAGS = env.ValHash.VALIDHASHTAGS


# async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chats = [x[0] for x in funcs.get_chats()]

#     chat = update.message.chat
#     if chat.id not in chats:
#         funcs.add_chat(chat.id, chat.title)

#     # получение всех хэштегов
#     mess_capt_entities = update.message.caption_entities
#     mess_entities = update.message.entities

#     # проверка есть ли хэштег
#     if mess_capt_entities or mess_entities:
#         fl = True
#         if mess_capt_entities:
#             # если есть фотка
#             hashtag_text = update.message.parse_caption_entity(mess_capt_entities[0])
#         else:
#             # если её нет
#             hashtag_text = update.message.parse_entity(mess_entities[0])
#             fl = False

#         if hashtag_text in VALIDHASHTAGS.keys():
#             # сохранение сообщения для пересылки
#             chat_id = update.message.chat.id

#             funcs.add_homework(chat_id, hashtag_text, update.message.id)
#             log.logger.info(
#                 "Saved %s from %s in %s",
#                 hashtag_text,
#                 update.message.from_user.username,
#                 update.message.chat.title,
#             )

#             if fl:
#                 return NEXT

#             return ConversationHandler.END

#         return ConversationHandler.END
#     else:
#         last_homework = funcs.get_last_homework(update.message.chat.id)

#         if last_homework:
#             funcs.add_homework(update.message.chat.id, last_homework, update.message.id)
#             return NEXT

#         return ConversationHandler.END
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import handlers.funcs
import handlers.log
import handlers.env

NEXT = ""
VALID_HASHTAGS = handlers.env.ValHash.VALIDHASHTAGS


async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save user's homework message."""

    chat = update.message.chat
    chat_id = chat.id
    chat_title = chat.title
    username = update.message.from_user.username

    # Check if the chat is already registered
    chats = [x[0] for x in handlers.funcs.get_chats()]
    if chat_id not in chats:
        handlers.funcs.add_chat(chat_id, chat_title)

    # Process caption and entities
    hashtag_text = None
    mess_capt_entities = update.message.caption_entities
    mess_entities = update.message.entities

    # проверка есть ли хэштег
    if mess_capt_entities or mess_entities:
        print(len(mess_capt_entities), len(mess_entities))
        if mess_capt_entities:
            # если есть фотка
            hashtag_text = update.message.parse_caption_entity(mess_capt_entities[0])
        else:
            # если её нет
            hashtag_text = update.message.parse_entity(mess_entities[0])

    if hashtag_text:
        # Check if the hashtag is valid
        if hashtag_text in VALID_HASHTAGS.keys():
            handlers.funcs.add_homework(chat_id, hashtag_text, update.message.id)

            # Log the saved homework
            handlers.log.logger.info(
                "Saved %s from %s in %s",
                hashtag_text,
                username,
                chat_title,
            )

            return NEXT

    # Save the last homework if no new homework is provided
    last_homework = handlers.funcs.get_last_homework(chat_id)
    if last_homework:
        handlers.funcs.add_homework(chat_id, last_homework, update.message.id)

    return ConversationHandler.END


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END
