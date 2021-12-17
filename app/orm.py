from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from functools import cached_property
from pprint import pprint

import psycopg

# Global database connection instance (import-time) (manages initialization and destruction)
_con = psycopg.connect(
    host="localhost",
    port="5432",
    user="postgres",
    password="postgres",
    dbname="postgres",
)

# Global cursor object
_cur = _con.cursor()


class Users:
    """Class representing database table operations (ORM)."""

    def get(self, *, id_=None, phone=None) -> User | None:
        if id_ is not None and phone is not None:
            return

        user = None

        if id_ is not None:
            _cur.execute(
                """
                SELECT id, first_name, last_name, phone, password, is_superuser FROM public.user
                WHERE id = %s
                """,
                (id_,),
            )
            user = _cur.fetchone()

        if phone is not None:
            _cur.execute(
                """
                SELECT id, first_name, last_name, phone, password, is_superuser FROM public.user
                WHERE phone = %s
                """,
                (phone,),
            )
            user = _cur.fetchone()

        if user is None:
            return

        id, first_name, last_name, phone, password, is_superuser = user
        return User(id, first_name, last_name, phone, password, is_superuser)

    def list(self):
        _cur.execute(
            "SELECT id, first_name, last_name, phone, password FROM public.user;"
        )
        return [User(*user) for user in _cur.fetchall()]

    def create(self):
        pass

    def delete(self):
        pass


class Clients:
    def get(self, user) -> Client | None:
        _cur.execute(
            """
        SELECT id, user, individual
        FROM public.client WHERE client.user = %s
        """,
            (user,),
        )
        client = _cur.fetchone()
        return client and Client(*client)


class Couriers:
    def get(self, user) -> Courier | None:
        _cur.execute(
            """
        SELECT id, user, vehicle, passport, employment_record, resident_place
        FROM public.courier WHERE courier.user = %s
        """,
            (user,),
        )
        courier = _cur.fetchone()
        return courier and Courier(*courier)


clients = Clients()


@dataclass(frozen=True)
class User:
    """Class representing user object/entity/row/data."""

    id: int
    first_name: str
    last_name: str
    phone: str
    password: str
    is_superuser: bool

    # Attributes derived from id

    @cached_property
    def is_client(self) -> bool:
        """Is client attribute (property) is derived form user id.
        Expensive to compute (requires database query) and not always needed.
        """
        return True if clients.get(self.id) else False

    @property
    def is_courier(self) -> bool:
        """Regular users can be either clients or couriers. Admin users can be neither."""
        return not self.is_client

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class Client:
    id: int
    _user: int
    individual: bool


@dataclass
class Courier:
    """Class representing courier row."""

    id: int
    _user: int
    _vehicle: int
    passport: str
    employment_record: str
    resident_place: str

    # def __post_init__(self):
    #     self.__user = None

    @cached_property
    def user(self) -> User | None:
        return users.get(id_=self._user)

        # _user init variable will be deleted after __init__
        # if self.__user is None:
        #     # Expensive action to do every time (and needs only when called at least one time)
        #     self.__user = None
        # return self.__user

    def __str__(self):
        return f'Courier "{self.user}"'


class Order:
    pass


class Orders:
    pass


class Comment:
    pass


class Comments:
    pass


class Address:
    pass


class Addresses:
    pass


users = Users()
orders = Orders()
comments = Comments()
addresses = Addresses()


# if __name__ == "__main__":
#     with psycopg.connect(
#         host="localhost",
#         port="5432",
#         user="postgres",
#         password="postgres",
#         dbname="postgres",
#     ) as con:
#         with con.cursor() as cur:
#             cur.execute("SELECT first_name, last_name FROM public.user;")
#             pprint(cur.fetchall())
