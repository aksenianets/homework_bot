from telegram import Bot, Update, constants
from telegram.ext import ContextTypes

import handlers.env

BOT_TOKEN = handlers.env.TgKeys.TOKEN


async def explain_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with Bot(BOT_TOKEN) as bot:
        await bot.send_message(
            chat_id=update.message.chat.id,
            parse_mode=constants.ParseMode.MARKDOWN_V2,
            text=f"Оо, привет\nЯ помогу вам быстро получать дамашку, которую вы сюда кинете\nДля начала, [напишите мне](https://t.me/give_my_homework_bot?start=first) и отправьте сюда сообщение с хэштегами",
        )
        await bot.send_message(
            chat_id=update.message.chat.id,
            parse_mode=constants.ParseMode.MARKDOWN_V2,
            text=f"Чтобы вы могли установить своё расписание, выберите одного ~жертву~ человека и пусть он напишет @aksenianets",
        )
        await bot.send_message(
            chat_id=update.message.chat.id,
            parse_mode=constants.ParseMode.MARKDOWN_V2,
            text=f"Теперь вы можете просто отправлять дз в этот чат и я её сохраню\nПользоваться мной можно ТОЛЬКО В ЛИЧКЕ",
        )


# by aksenianets
