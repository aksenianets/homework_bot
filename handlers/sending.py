from telegram import Bot, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from datetime import datetime

from handlers import funcs, env, log

BOT_TOKEN = env.TgKeys.TOKEN
VALIDHASHTAGS = env.ValHash.VALIDHASHTAGS
SUBJECT = ""


async def send_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.logger.info("sendall %s", update.message.from_user.username)

    user_chat = funcs.get_user_info(update.message.from_user.id)[0][1]
    need_to_send = funcs.get_schedule(user_chat, datetime.now().weekday() + 1)
    need_to_send.append("#расписание")
    fl = True

    no_homework = []
    if need_to_send:
        for x in need_to_send:
            homework = funcs.get_homework(user_chat, x)
            if homework:
                if len(homework) == 1:
                    try:
                        async with Bot(BOT_TOKEN) as bot:
                            await bot.forward_message(
                                chat_id=update.effective_chat.id,
                                from_chat_id=user_chat,
                                message_id=homework[0][0],
                            )

                            date = str(homework[0][1])
                            date = f"{date[3:5]}.{date[1:3]}"
                            await bot.send_message(
                                chat_id=update.effective_chat.id,
                                text=f"ДЗ от {date}",
                            )
                    except:
                        no_homework.append(x)
                else:
                    for x in homework:
                        try:
                            async with Bot(BOT_TOKEN) as bot:
                                # пересылание дз
                                await bot.forward_message(
                                    chat_id=update.effective_chat.id,
                                    from_chat_id=user_chat,
                                    message_id=x[0],
                                )

                                # отправка даты пересылаемого сообщения
                                date = str(x[1])
                                date = f"{date[3:5]}.{date[1:3]}"
                                await bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text=f"ДЗ от {date}",
                                )
                        except:
                            no_homework.append(x)
            else:
                no_homework.append(x)

    if fl:
        await update.message.reply_text(
            f"Упс, дз по {', '.join(no_homework)} отправить не вышло((",
            reply_markup=ReplyKeyboardRemove(),
        )


async def ask_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.logger.info("asksubject %s", update.message.from_user.username)

    reply_keyboard = funcs.grouper(sorted(VALIDHASHTAGS.values(), reverse=True), 4)

    subjects = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Чего хочешь добрый человек?", reply_markup=subjects
    )

    return SUBJECT


async def send_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.logger.info("sendme %s", update.message.from_user.username)

    subject = update.message.text

    if subject not in VALIDHASHTAGS.values():
        await update.message.reply_text(
            "Чегось? Ась?\nЯ такого не слышал, попробуй ещё разок"
        )
    else:

        async with Bot(BOT_TOKEN) as bot:
            await bot.delete_messages(
                chat_id=update.message.chat.id,
                message_ids=[update.message.id, update.message.id - 1],
            )

        subject = list(VALIDHASHTAGS.keys())[
            list(VALIDHASHTAGS.values()).index(subject)
        ]

        user_chat = funcs.get_user_info(update.message.from_user.id)[0][1]
        homework = funcs.get_homework(user_chat, subject)

        if homework:
            if len(homework) == 1:
                try:
                    async with Bot(BOT_TOKEN) as bot:
                        await bot.forward_message(
                            chat_id=update.effective_chat.id,
                            from_chat_id=user_chat,
                            message_id=homework[0][0],
                        )

                        date = str(homework[0][1])
                        date = f"{date[3:5]}.{date[1:3]}"
                        await bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=f"ДЗ от {date}",
                        )
                except:
                    await update.message.reply_text(
                        f"Ойой, технические шоколадки",
                        reply_markup=ReplyKeyboardRemove(),
                    )
            else:
                for x in homework:
                    try:
                        async with Bot(BOT_TOKEN) as bot:
                            await bot.forward_message(
                                chat_id=update.effective_chat.id,
                                from_chat_id=user_chat,
                                message_id=x[0],
                            )

                            date = str(x[1])
                            date = f"{date[3:5]}.{date[1:3]}"

                            await bot.send_message(
                                chat_id=update.effective_chat.id,
                                text=f"ДЗ от {date}",
                            )
                    except:
                        await update.message.reply_text(
                            f"Ойой, технические шоколадки",
                            reply_markup=ReplyKeyboardRemove(),
                        )
        else:
            await update.message.reply_text(
                f"Упс, дз по {subject} отправить не вышло((",
                reply_markup=ReplyKeyboardRemove(),
            )

        return ConversationHandler.END


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_markdown_v2(
        text="[Stop, wait a minute](https://youtu.be/w_Fk0i9Vq_o)\ \nКороче, остановил действие",
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )

    return ConversationHandler.END


# by aksenianets
