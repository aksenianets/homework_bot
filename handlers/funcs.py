from datetime import datetime
import sqlite3
from itertools import zip_longest
import shutil

from handlers import env, log

# import env

VALIDHASHTAGS = env.ValHash.VALIDHASHTAGS
ABSOLUTEPATH = env.AbsPath.ABSOLUTEPATH
PATHTODB = ABSOLUTEPATH + "data.db"


def check_all() -> bool:
    for table in ["Chats", "Users", "Messages", "Schedule"]:
        res = sqlite3.connect(PATHTODB).execute(f"SELECT * FROM {table}")
        res = [x for x in res if None not in x]
        if not res:
            return False

    return True


def clear_all() -> None:
    shutil.copy(PATHTODB, ABSOLUTEPATH + "data_copy.db")
    with sqlite3.connect(PATHTODB) as con:
        for table in ["Chats", "Users", "Messages", "Schedule"]:
            con.executescript(f"DELETE FROM {table}")


# actions with admins
def make_admin(user_id: int) -> None:
    make_query = f"""
        UPDATE Users
        SET (userid, chatid, admin) = (userid, chatid, 1)
        WHERE userid = {user_id}
    """

    with sqlite3.connect(PATHTODB) as con:
        con.executescript(make_query)


def unadmin_all() -> None:
    un_query = f"""
        UPDATE Users
        SET (userid, chatid, admin) = (userid, chatid, 0)
    """

    with sqlite3.connect(PATHTODB) as con:
        con.executescript(un_query)


def check_admin(user_id: int) -> None:
    get_query = """SELECT userid FROM Users WHERE admin=1"""

    res = sqlite3.connect(PATHTODB).execute(get_query)
    res = [x for x in res if None not in x]

    return (user_id,) in res


# actions with users
def add_user(user_id: int, chat_id: int) -> None:
    try:
        add_query = f"""
            INSERT INTO Users
            VALUES(?, ?, ?), 
            ({user_id}, "{chat_id}", 0)
        """

        with sqlite3.connect(PATHTODB) as con:
            con.executescript(add_query)
    except:
        add_query = f"""
            UPDATE Users
            SET (userid, chatid, admin) = ({user_id}, {chat_id}, 0)
            WHERE userid = {user_id}
        """

        with sqlite3.connect(PATHTODB) as con:
            con.executescript(add_query)


def get_users() -> list[tuple]:
    get_query = "SELECT * FROM Users;"

    res = sqlite3.connect(PATHTODB).execute(get_query)
    res = [x for x in res if None not in x]

    return res


def get_user_info(user_id: int) -> tuple:
    get_query = f"SELECT * FROM Users WHERE userid = {user_id};"

    res = sqlite3.connect(PATHTODB).execute(get_query)
    res = [x for x in res if None not in x]

    return res


# actions with chats
def add_chat(chat_id: int, chat_name: str) -> None:
    try:
        add_query = f"""
            INSERT INTO Chats
            VALUES(?, ?), 
            ({chat_id}, "{chat_name}")
        """

        with sqlite3.connect(PATHTODB) as con:
            con.executescript(add_query)
    except:
        update_query = f"""
            UPDATE Chats
            SET (chatid, chatname) = ({chat_id}, "{chat_name}")
            WHERE chatid = {chat_id}
        """

        with sqlite3.connect(PATHTODB) as con:
            con.executescript(update_query)


def delete_chat(chat_id: int) -> None:
    with sqlite3.connect(PATHTODB) as con:
        con.executescript(f"""DELETE FROM Chats WHERE chatid={chat_id}""")
        con.executescript(f"""DELETE FROM Users WHERE chatid={chat_id}""")
        con.executescript(f"""DELETE FROM Messages WHERE chatid={chat_id}""")
        con.executescript(f"""DELETE FROM Schedule WHERE chatid={chat_id}""")


def get_chats() -> list[tuple]:
    get_query = """SELECT * FROM Chats"""

    res = sqlite3.connect(PATHTODB).execute(get_query)
    res = [x for x in res if None not in x]

    return res


def get_chatname(chat_id: int) -> str:
    get_query = f"""SELECT chatname FROM Chats WHERE chatid={chat_id}"""

    res = sqlite3.connect(PATHTODB).execute(get_query)
    res = [x for x in res if None not in x]

    return res


# actions with homework
def add_homework(chat_id: int, subject_id: str, message_id: int) -> None:
    try:
        add_query = f"""
            INSERT INTO Messages
            VALUES(?, ?, ?, ?, ?), 
            ({message_id}, {int("9" + datetime.now().strftime("%m%d%Y"))} , {chat_id}, "{subject_id}", "{message_id}.{chat_id}")
        """

        with sqlite3.connect(PATHTODB) as con:
            con.executescript(add_query)
    except:
        update_query = f"""
            UPDATE Messages
            SET (messageid, data, chatid, subjectid, id) = ({message_id}, data, chatid, {subject_id}, "{message_id}.{chat_id}")
            WHERE messageid = {message_id}
        """

        with sqlite3.connect(PATHTODB) as con:
            con.executescript(update_query)


def get_homework(chat_id: int, subject_id: str) -> list[tuple]:
    get_query = f"""
        SELECT messageid, data, subjectid FROM Messages
        WHERE chatid={chat_id}
        AND subjectid="{subject_id}"
        ORDER BY -data
    """

    res = sqlite3.connect(PATHTODB).execute(get_query)
    res = [x for x in res if None not in x]

    if res:
        prev = res[0][1]
        cnt = 0
        for x in res:
            if x[1] != prev:
                break
            prev = x[1]
            cnt += 1

        return res[:cnt]

    return False


def get_last_homework(chat_id: int) -> str:
    get_query = f"""
        SELECT messageid, subjectid FROM Messages
        WHERE chatid={chat_id}
        ORDER BY data
    """

    res = sqlite3.connect(PATHTODB).execute(get_query)
    res = [x for x in res if None not in x]

    if res:
        return res[-1][0]
    return False


# actions with schedule
def get_schedule(chat_id: int, weekday: int) -> list[str]:
    if weekday >= 5:
        weekday = 0

    get_query = f"""
        SELECT subjects FROM Schedule
        WHERE chatid = {chat_id} AND weekday = {weekday}
    """

    res = sqlite3.connect(PATHTODB).execute(get_query)
    res = [x for x in res if None not in x]

    if res:
        res = eval(res[0][0])
        cnt = 0
        for x in res:
            subject = list(VALIDHASHTAGS.keys())[list(VALIDHASHTAGS.values()).index(x)]
            res[cnt] = subject
            cnt += 1

    return res


def set_schedule(chat_id: int, schedule: list[list[str]]) -> None:
    cnt = 0
    sch_check = get_schedule(chat_id, 0)

    if not sch_check:
        for x in schedule:
            add_query = f"""
                INSERT INTO Schedule
                VALUES(?, ?, ?),
                ({chat_id}, {cnt}, "{x}")
            """

            cnt += 1
            with sqlite3.connect(PATHTODB) as con:
                con.executescript(add_query)
    else:
        for x in schedule:
            add_query = f"""
                UPDATE Schedule
                SET (chatid, weekday, subjects) = (chatid, weekday, "{x}")
                WHERE chatid = {chat_id} AND weekday = {cnt}
            """

            cnt += 1
            with sqlite3.connect(PATHTODB) as con:
                con.executescript(add_query)


def delete_schedule(chat_id: int) -> None:
    delete_query = f"DELETE FROM Schedule WHERE chatid = {chat_id}"

    with sqlite3.connect(PATHTODB) as con:
        con.executescript(delete_query)


# other
def grouper(iterable: list, n: int) -> list[str]:
    args = [iter(iterable)] * n
    result = zip_longest(*args)

    result = [list(pair) for pair in result if pair[0] is not None]
    if None in result[-1]:
        result[-1] = result[-1][: result[-1].index(None)]

    return result
