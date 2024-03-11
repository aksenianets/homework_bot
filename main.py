from telegram import MessageEntity
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    # ChatMemberHandler,
    CallbackQueryHandler,
    filters,
)
import shutil

from handlers import sending, start, admin, homework, env, funcs, senderror

if funcs.check_all():
    shutil.copy(
        env.AbsPath.ABSOLUTEPATH + "data.db", env.AbsPath.ABSOLUTEPATH + "data_copy.db"
    )

if __name__ == "__main__":
    application = ApplicationBuilder().token(env.TgKeys.TOKEN).build()

    application.add_handler(CallbackQueryHandler(start.button))

    # save homework
    homework_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                (
                    filters.CaptionEntity(MessageEntity.HASHTAG)
                    | filters.Entity(MessageEntity.HASHTAG)
                )
                & (
                    filters.ChatType.GROUP
                    | filters.ChatType.SUPERGROUP
                    | filters.Chat(funcs.get_admins())
                ),
                homework.save,
            )
        ],
        states={
            homework.NEXT: [
                MessageHandler(
                    filters.PHOTO
                    & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP),
                    homework.save,
                )
            ]
        },
        fallbacks=[MessageHandler(filters.TEXT, homework.stop)],
    )
    application.add_handler(homework_handler)

    # user commands
    application.add_handler(
        CommandHandler("start", start.start, filters.ChatType.PRIVATE)
    )
    application.add_handler(
        CommandHandler("sendall", sending.send_all, filters.ChatType.PRIVATE)
    )
    send_subject_handler = ConversationHandler(
        entry_points=[
            CommandHandler("sendme", sending.ask_subject, filters.ChatType.PRIVATE)
        ],
        states={
            sending.SUBJECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, sending.send_subject)
            ]
        },
        fallbacks=[MessageHandler(filters.COMMAND, sending.stop)],
    )
    application.add_handler(send_subject_handler)

    # admin commands

    # deleted - i dont know, but it breaks bot((
    # application.add_handler(
    #     CommandHandler("showchats", getchats.show_chats, filters.ChatType.PRIVATE)
    # )
    application.add_handler(
        CommandHandler("getadmin", admin.get_admin_rights, filters.ChatType.PRIVATE)
    )
    schedule_handler = ConversationHandler(
        entry_points=[
            CommandHandler("setschedule", admin.ask_shedule, filters.ChatType.PRIVATE)
        ],
        states={
            admin.SCHEDULE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin.set_schedule)
            ]
        },
        fallbacks=[MessageHandler(filters.COMMAND, admin.stop)],
    )
    application.add_handler(schedule_handler)
    application.add_handler(
        CommandHandler("cleardb", admin.clear_db, filters.ChatType.PRIVATE)
    )
    application.add_handler(
        CommandHandler("deletechat", admin.delete_chat, filters.ChatType.PRIVATE)
    )
    application.add_handler(
        CommandHandler("unadmin", admin.unadmin_all, filters.ChatType.PRIVATE)
    )
    send_to_all_users_handler = ConversationHandler(
        entry_points=[CommandHandler("SAU", admin.ask_text, filters.ChatType.PRIVATE)],
        states={
            admin.SEND: [MessageHandler(~filters.COMMAND, admin.send_to_all_users)]
        },
        fallbacks=[MessageHandler(filters.COMMAND, admin.stop)],
    )
    application.add_handler(send_to_all_users_handler)

    # other
    application.add_error_handler(senderror.error_handler)

    application.add_handler(CommandHandler("sendwithids", admin.send_all_with_ids))
    # deleted - i dont know, but it breaks bot((
    # application.add_handler(
    #     ChatMemberHandler(getchats.track_chats, ChatMemberHandler.MY_CHAT_MEMBER)
    # )

    application.run_polling()
