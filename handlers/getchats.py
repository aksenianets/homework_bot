from typing import Optional, Tuple

from telegram import Chat, ChatMember, ChatMemberUpdated, Update
from telegram.ext import ContextTypes

from log import logger
import funcs as funcs


def extract_status_change(
    chat_member_update: ChatMemberUpdated,
) -> Optional[Tuple[bool, bool]]:

    status_change = chat_member_update.difference().get("status")

    old_is_member, new_is_member = chat_member_update.difference().get(
        "is_member", (None, None)
    )

    if status_change is None:
        return None

    old_status, new_status = status_change

    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)

    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = extract_status_change(update.my_chat_member)

    if result is None:
        return

    was_member, is_member = result
    cause_name = update.effective_user.full_name
    chat = update.effective_chat

    if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logger.info("%s added the bot to the %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).add(chat.title)
            funcs.add_chat(chat.id, str(chat.title))
        elif was_member and not is_member:
            logger.info("%s removed the bot from the %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).discard(chat.title)
            funcs.delete_chat(chat.id)
    elif not was_member and is_member:
        logger.info("%s added the bot to the channel %s", cause_name, chat.title)
        context.bot_data.setdefault("channel_ids", set()).add(chat.id)
        funcs.add_chat(chat.id, str(chat.title))
    elif was_member and not is_member:
        logger.info("%s removed the bot from the channel %s", cause_name, chat.title)
        context.bot_data.setdefault("channel_ids", set()).discard(chat.id)
        funcs.delete_chat(chat.id)


async def show_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    groups = [x[1] for x in funcs.get_chats()]
    text = f"Member of: {', '.join(groups) or '-'}"
    await update.effective_message.reply_text(text)
