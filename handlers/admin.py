from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import ContextTypes, ConversationHandler

import sqlite3

from handlers import funcs, log, env

BOT_TOKEN = env.TgKeys.TOKEN
PASSWORD = env.Passw.PASSWORD
ADMINPASSWORD = env.AdmPassw.ADMINPASSWORD
VALIDHASHTAGS = env.ValHash.VALIDHASHTAGS
SCHEDULE, SEND = "", ""

ABSOLUTEPATH = env.AbsPath.ABSOLUTEPATH
PATHTODB = ABSOLUTEPATH + "data.db"


async def get_admin_rights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.logger.warning("getadmin %s", update.message.from_user.id)

    if update.message.text == f"/getadmin {PASSWORD}":
        if not funcs.check_admin(update.message.from_user.id):
            log.logger.info("%s now admin", update.message.from_user.username)
            funcs.make_admin(update.message.from_user.id)

            await update.message.reply_text(
                "Теперь ты можешь использовать\n/setschedule"
            )
        else:
            await update.message.reply_text("Да ты уже ведь админ, бро")

    else:
        await update.message.reply_text("Неа, не угадал пароль;)")


async def unadmin_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.logger.warning("unadmin %s", update.message.from_user.id)
    if update.message.text == f"/unadmin {ADMINPASSWORD}":
        if funcs.check_admin(update.message.from_user.id):
            log.logger.warning(
                "All admins removed by %s", update.message.from_user.username
            )
            funcs.unadmin_all()
            await update.message.reply_text(
                "Ничего себе, что наделал\nТеперь админов нет, press F"
            )


async def ask_shedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.logger.warning("askschedule %s", update.message.from_user.id)

    if funcs.check_admin(update.message.from_user.id):
        text = (
            "Задайте расписание уроков для ДЗ.\n",
            "Расписание должно состоять из 5 строк.\n",
            "Уроки в строке не должны повторяться, должны идти через пробел.\n",
            "Сокращения такие же, как в примере\n",
            "Или: Био, Экон, МХК, Геогр\n",
            "Пример:",
        )
        await update.message.reply_text(text="".join(text))
        example = (
            "Мат Инф Рус Хим Ист\n",
            "Физ Мат Общ Англ Лит\n",
            "Инф Физ Мат Лит Англ\n",
            "Инф Мат Общ Хим Родн Про Астр\n",
            "Инф Физ Граф Инт Англ Ист Обж",
        )
        await update.message.reply_text(text="".join(example))

        return SCHEDULE
    else:
        await update.message.reply_text("Да ты ведь не админ, прикинь")

        return ConversationHandler.END


async def set_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.logger.warning("setschedule %s", update.message.from_user.id)

    schedule = update.message.text
    schedule = [x.split() for x in schedule.split("\n")]

    if len(schedule) != 5:
        await update.message.reply_text(
            "Ничего не понял, ты явно написал что-то не так\nДавай ещё разок или /stop"
        )
    else:
        user_chat = funcs.get_user_info(update.message.from_user.id)[0][1]
        chatname = funcs.get_chatname(user_chat)[0][0]

        check = []
        for x in schedule:
            check.append(all(list(map(lambda y: y in VALIDHASHTAGS.values(), x))))

        if all(check):
            funcs.set_schedule(user_chat, schedule)
            log.logger.info("Schedule has been set for %s", chatname)

            await update.message.reply_text(
                f"Агаа, для {chatname} расписание запомнил!"
            )

            async with Bot(BOT_TOKEN) as bot:
                await bot.delete_messages(
                    chat_id=update.message.chat.id,
                    message_ids=[update.message.id - 1, update.message.id - 2],
                )

            return ConversationHandler.END
        else:
            await update.message.reply_text(
                "Ничего не понял, ты явно написал что-то не так\nДавай ещё разок или /stop"
            )


async def delete_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.logger.warning("deletechat %s", update.message.from_user.id)

    user_chat = funcs.get_user_info(update.message.from_user.id)[0][1]
    chats = dict(funcs.get_chats())

    if funcs.check_admin(update.message.from_user.id):
        reply_list = [
            [InlineKeyboardButton("Да", callback_data="Да")],
            [InlineKeyboardButton("Нет", callback_data="Нет")],
        ]
        reply_markup = InlineKeyboardMarkup(reply_list)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Тактактак, ты точно хочешь снизвести {chats[user_chat]}?",
            reply_markup=reply_markup,
        )


async def ask_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if funcs.check_admin(update.message.from_user.id):
        await update.message.reply_text("Ну тогда давай, что нужно всем переслать")

        return SEND

    return ConversationHandler.END


async def send_to_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = [x[0] for x in funcs.get_users()]

    chat_id = update.message.chat.id
    message_id = update.message.id

    fl = True
    for x in users:
        async with Bot(BOT_TOKEN) as bot:
            try:
                await bot.forward_message(
                    chat_id=x,
                    from_chat_id=chat_id,
                    message_id=message_id,
                    protect_content=True,
                )
            except:
                await update.message.reply_text(
                    f"Ой, вот ему(ей) отправить не получилось - {x}"
                )
                fl = False

    if fl:
        async with Bot(BOT_TOKEN) as bot:
            await bot.delete_messages(
                chat_id=update.message.chat.id,
                message_ids=[update.message.id, update.message.id - 1],
            )

    log.logger.info(
        "Message sent to all users by %s", update.message.from_user.username
    )
    await update.message.reply_text(f"Готово, босс, всем отправил!")

    return ConversationHandler.END


async def send_all_with_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_query = f"""
        SELECT chatid, messageid FROM Messages
        ORDER BY data
    """

    res = sqlite3.connect(PATHTODB).execute(get_query)
    res = [x for x in res if None not in x]

    async with Bot(BOT_TOKEN) as bot:
        for x in res:
            chat_id = x[0]
            message_id = x[1]
            try:
                await bot.forward_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=chat_id,
                    message_id=message_id,
                )
                await update.message.reply_text(message_id)
            except:
                await update.message.reply_text(f"Oops {message_id}")


async def clear_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == f"/cleardb {ADMINPASSWORD}":
        if funcs.check_admin(update.message.from_user.id):
            funcs.clear_all()
            await update.message.reply_text("БД уничтожена((")
            log.logger.warning("DB is cleared by %s", update.message.from_user.username)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.logger.warning("cancel %s", update.message.from_user.id)

    await update.message.reply_markdown_v2(
        text="[Stop, wait a minute](https://youtu.be/w_Fk0i9Vq_o)\nКороче, остановил действие",
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


# by aksenianets
