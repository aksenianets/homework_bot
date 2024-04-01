from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from telegram.ext import ContextTypes

from handlers import log
from handlers import funcs
from handlers import env

VALIDHASHTAGS = env.ValHash.VALIDHASHTAGS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.logger.info("start %s", update.message.from_user.username)

    reply_markup = [x[1] for x in funcs.get_chats()]
    users = funcs.get_users()[0]

    text = f"Привет {update.message.from_user.username}, из какого чата будешь?"
    if update.message.text != "/start first" and update.message.from_user.id in users:
        reply_markup.append("Отмена")
        text = "В какой чат хочешь перейти?"
    if reply_markup:
        reply_markup = funcs.grouper(reply_markup, 2)

        reply_list = []
        cnt = 1

        for x in reply_markup:
            temporary_list = []
            for y in x:
                btn = InlineKeyboardButton(y, callback_data=y)
                temporary_list.append(btn)
                cnt += 1

            reply_list.append(temporary_list)

        reply_markup = InlineKeyboardMarkup(reply_list)

        if update.message.text == "/start first":
            await update.message.reply_text(
                "Отправьте следующее сообщение в чат вашего класса\nВ ЕДИНСТВЕННОМ ЭКЗЕМПЛЯРЕ"
            )
            hashs = """
            #расписание\n#математика\n#русский\n#информатика\n#общага\n#экономика\n#МХК\n#право\n#биология\n#химия\n#литература\n#история\n#обж\n#английский\n#родной\n#проектнаядеятельность\n#интуиция\n#физика\n#графы\n#астрономия\n#география\n#правочеловека
            """
            await update.message.reply_text(text=hashs)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="А после этого напишите мне /start",
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=reply_markup,
            )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chat_hr = query.data

    log.logger.info("button %s, query=%s", query.from_user.username, query.data)

    if chat_hr != "Отмена" and chat_hr != "Нет":
        if chat_hr != "Да":
            chats = funcs.get_chats()
            chats = [x[::-1] for x in chats]
            chats = dict(chats)

            chat = chats[chat_hr]

            users = funcs.get_users()

            users1 = [(x[0], x[2]) for x in users]
            users1 = dict(users1)
            users2 = [(x[0], x[1]) for x in users]
            users2 = dict(users2)

            user_id = query.from_user.id

            text = f"Вы добавлены в {chat_hr}"
            if users1:
                if user_id in users1:
                    if chat == users2[user_id]:
                        text = f"Вы уже в {chat_hr}"
                    else:
                        if users1[user_id] == 1:
                            text = f"Вы перемещены в {chat_hr}\nВы больше не админ"
                        else:
                            text = f"Вы перемещены в {chat_hr}"

                        log.logger.info(
                            "New user %s in %s", query.from_user.username, chat_hr
                        )

            funcs.add_user(user_id, chat)

            await query.edit_message_text(text=text)
        else:
            user_chat = funcs.get_user_info(update.message.from_user.id)[0][1]
            chats = dict(funcs.get_chats())

            funcs.delete_chat(user_chat)
            await query.edit_message_text(
                f"{chats[user_chat]} удалён из бота\nТеперь используйте /start"
            )

            log.logger.warning("Chat %s has been deleted", chats[user_chat])
    else:
        await query.edit_message_text("Действие отменено")


# by aksenianets
