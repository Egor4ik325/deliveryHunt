from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from datetime import datetime, timedelta
from functools import cache, cached_property
from pprint import pprint
from typing import Callable
from uuid import UUID

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

    def get(self, *, id_: int = None, phone: str = None) -> User | None:
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
        return User(id, first_name, last_name, phone, password, is_superuser)  # type: ignore

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
    def get(self, user: User) -> Client | None:
        _cur.execute(
            """
        SELECT id, "user", individual
        FROM public.client WHERE client."user" = %s
        """,
            (user.id,),
        )
        client = _cur.fetchone()
        return client and Client(*client)

    def get_by_id(self, id_: int) -> Client | None:
        _cur.execute(
            """
        SELECT id, "user", individual
        FROM public.client WHERE id = %s
        """,
            (id_,),
        )
        client = _cur.fetchone()
        return client and Client(*client)


class Couriers:
    def get(self, user: User) -> Courier | None:
        _cur.execute(
            """
        SELECT id, "user", vehicle, passport, employment_record, resident_place
        FROM public.courier WHERE courier.user = %s
        """,
            (user.id,),
        )
        courier = _cur.fetchone()
        return courier and Courier(*courier)

    def get_by_id(self, id_: int) -> Courier | None:
        _cur.execute(
            """
        SELECT id, "user", vehicle, passport, employment_record, resident_place
        FROM public.courier WHERE courier.id = %s
        """,
            (id_,),
        )
        courier = _cur.fetchone()
        return courier and Courier(*courier)


class Orders:
    def list(self, *, client: Client = None) -> list[Order]:
        if client is not None:
            _cur.execute(
                """
                SELECT id, client, courier, create_time, address_from, address_to, weight, comment,
                max_delivery_time, take_time, deliver_time, delivered, rate
                FROM public.order
                WHERE client = %s
                """,
                (client.id,),
            )
            orders = _cur.fetchall()
            return [Order(*order) for order in orders] if orders is not None else []

        return []

    def list_free(self) -> list[Order]:
        _cur.execute(
            """
            SELECT id, client, courier, create_time, address_from, address_to, weight, comment,
            max_delivery_time, take_time, deliver_time, delivered, rate
            FROM public.order
            WHERE public.order.courier is NULL;
            """
        )
        orders = _cur.fetchall()
        return [Order(*order) for order in orders] if orders is not None else []

    def list_taken(self, courier: Courier) -> list[Order]:
        _cur.execute(
            """
            SELECT id, client, courier, create_time, address_from, address_to, weight, comment,
            max_delivery_time, take_time, deliver_time, delivered, rate
            FROM public.order
            WHERE public.order.courier = %s;
            """,
            (courier.id,),
        )
        orders = _cur.fetchall()
        return [Order(*order) for order in orders] if orders is not None else []

    def get(self, id_: str) -> Order | None:
        _cur.execute(
            """
            SELECT id, client, courier, create_time, address_from, address_to, weight, comment,
            max_delivery_time, take_time, deliver_time, delivered, rate
            FROM public.order
            WHERE public.order.id = %s;
            """,
            (id_,),
        )
        order = _cur.fetchone()
        return order and Order(*order)


class Comments:
    pass


class Table:
    """Base class for common table functionality."""

    fields = []

    def list(self):
        pass

    def get(self):
        pass

    def update(self):
        pass


class Addresses:
    pass


class Administration:
    pass


clients = Clients()
couriers = Couriers()
users = Users()
orders = Orders()
comments = Comments()
addresses = Addresses()


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
    def client(self) -> Client | None:
        return clients.get(self)

    @cached_property
    def courier(self) -> Courier | None:
        return couriers.get(self)

    @cached_property
    def is_client(self) -> bool:
        """Is client attribute (property) is derived form user id.
        Expensive to compute (requires database query) and not always needed.
        """
        return True if self.client else False

    @property
    def is_courier(self) -> bool:
        """Regular users can be either clients or couriers. Admin users can be neither."""
        return True if self.courier else False

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class Client:
    id: int
    _user: int
    individual: bool

    @cached_property
    def user(self) -> User | None:
        return users.get(id_=self._user)

    def __str__(self):
        return f'Client "{self.user}"'


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


@dataclass(frozen=True)
class Order:
    id: UUID
    _client: int
    _courier: int | None
    create_time: datetime
    _address_from: int
    _address_to: int
    weight: float | None
    _comment: int | None
    max_delivery_time: timedelta
    take_time: datetime | None
    delivery_time: datetime | None
    delivered: bool | None
    rate: int | None

    @cached_property
    def client(self) -> Client | None:
        return clients.get_by_id(self._client)

    @cached_property
    def courier(self) -> Courier | None:
        if self._courier is not None:
            return couriers.get_by_id(self._courier)

    def address_from(self):
        pass

    def address_to(self):
        pass

    def comment(self):
        pass

    def __str__(self):
        return f"Order #{self.id}"


class Comment:
    pass


class Address:
    pass
