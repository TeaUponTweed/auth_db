import os
import random
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional, Tuple


def get_connection(db_file: Optional[str] = None) -> sqlite3.Connection:
    if db_file is None:
        db_file = os.environ["DB_FILE_LOC"]
    return sqlite3.connect(db_file, isolation_level=None)


@contextmanager
def transaction(conn):
    # We must issue a "BEGIN" explicitly when running in auto-commit mode.
    conn.execute("BEGIN")
    try:
        # Yield control back to the caller.
        yield
    except:
        conn.rollback()  # Roll back all changes if an exception occurs.
        raise
    else:
        conn.commit()


def init_db(db_file: str, schema_file: str) -> str:
    conn = get_connection(db_file)
    conn.execute("pragma journal_mode=wal")
    with open(schema_file) as fi:
        schema = fi.read()
        with transaction(conn):
            conn.executescript(schema)
        return schema


@dataclass
class User:
    email: str
    password: str


def make_new_user(user: User, conn: Optional[sqlite3.Connection] = None) -> int:
    if conn is None:
        conn = get_connection()
    with transaction(conn):
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users(email,password)
            VALUES (?,?)
            ON CONFLICT DO NOTHING
            """,
            (
                user.email,
                user.password,
            ),
        )
    user_id = cursor.lastrowid
    if user_id == 0:
        with transaction(conn):
            cursor.execute(
                """
                SELECT rowid from users
                where email = ?
                """,
                (user.email,),
            )
            (user_id,) = cursor.fetchone()
    return user_id


def get_user_id(email: str, conn: Optional[sqlite3.Connection] = None) -> Optional[int]:
    if conn is None:
        conn = get_connection()
    with transaction(conn):
        res = conn.execute(
            "SELECT rowid from users WHERE users.email = ?",
            (email,),
        )
        user_id = res.fetchone()
    if user_id is not None:
        return user_id[0]
    return None


def validate_user(
    email: str, conn: Optional[sqlite3.Connection] = None
) -> Optional[str]:
    if conn is None:
        conn = get_connection()
    with transaction(conn):
        res = conn.execute(
            """
            SELECT rowid, password from users
            WHERE users.email = ?
            """,
            (email,),
        )
        res = res.fetchone()
    if res is None:
        return None
    else:
        return res[1]


def get_user(user_id: int, conn: Optional[sqlite3.Connection] = None) -> Optional[User]:
    if user_id is None:
        return None
    q = """
    SELECT
    email, password
    FROM users
    where rowid = ?
    """
    if conn is None:
        conn = get_connection()
    with transaction(conn):
        cursor = conn.cursor()
        cursor.execute(q, (user_id,))
        user = cursor.fetchone()
    if not user:
        return None
    else:
        email, password = user
        return User(
            email=email,
            password=password,
        )


def reset_pw(email: str, conn: Optional[sqlite3.Connection] = None) -> Optional[str]:
    user = get_user(get_user_id(email=email, conn=conn), conn=conn)
    if user is None:
        print(f"Unknown email {email}")
        return None

    if conn is None:
        conn = get_connection()
    # mint token
    time.sleep(random.random())
    token = str(uuid.uuid4())
    # insert into db
    with transaction(conn):
        conn.execute(
            "INSERT INTO pw_reset(email,token,reset_time) values (?, ?, ?) ON CONFLICT DO NOTHING",
            (
                email,
                int(time.time()),
                token,
            ),
        )
    with transaction(conn):
        # update on replace not always supported
        conn.execute(
            "UPDATE pw_reset SET token = ?, reset_time = ? where  email = ?",
            (
                token,
                int(time.time()),
                email,
            ),
        )

    # reset pw
    with transaction(conn):
        res = conn.execute("UPDATE users SET password = NULL WHERE email = ?", (email,))
    return token


def check_token(
    token: str, conn: Optional[sqlite3.Connection] = None
) -> Optional[User]:
    if conn is None:
        conn = get_connection()

    with transaction(conn):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT email, reset_time from pw_reset where token = ?", (token,)
        )
        res = cursor.fetchone()
    if res:
        (email, reset_time) = res
        user = get_user(get_user_id(email=email, conn=conn), conn=conn)
        if user is None:
            print(f"Unknown email {email}")
            return None
        if (time.time() - reset_time) > 24 * 60 * 60:
            print("Password reset timed out")
            return None
        return user
    else:
        print(f"No matching token {token}")
        return None


def update_password(email: str, pw: str, conn: Optional[sqlite3.Connection] = None):
    if conn is None:
        conn = get_connection()
    with transaction(conn):
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? where email = ?", (pw, email))
