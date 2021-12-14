from dataclasses import dataclass
from pprint import pprint

import psycopg


@dataclass
class User:
    first_name: str
    last_name: str


def get_users() -> list[User]:
    with psycopg.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="postgres",
        dbname="postgres",
    ) as con:
        with con.cursor() as cur:
            cur.execute("SELECT first_name, last_name, phone  FROM public.user;")
            return [
                User(first_name=user[0], last_name=user[1]) for user in cur.fetchall()
            ]


if __name__ == "__main__":
    with psycopg.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="postgres",
        dbname="postgres",
    ) as con:
        with con.cursor() as cur:
            cur.execute("SELECT first_name, last_name FROM public.user;")
            pprint(cur.fetchall())
