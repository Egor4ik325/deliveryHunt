import csv
import random
from os import write
from typing import Generator
from uuid import uuid4

import argon2
import faker
import fire

courier_passports = [
    "3198329812",
    "5929892929",
    "4892398998",
    "2389482898",
    "8429830082",
    "4812347832",
    "3742751811",
    "7483829358",
]


class Generator:
    fake = faker.Faker(locale=["en", "ru"])
    ph = argon2.PasswordHasher()

    def __init__(self, count: int):
        self.count = count

    def __call__(self, table_name: str) -> None:
        """Calls appropriate method to get list of rows and than writes to CSV file.

        Returns:
        - (void) side effect on file system
        """

        with open(f"{table_name}.csv", "w") as f:
            writer = csv.writer(f)

            # Write generated row immediately
            rows = getattr(self, table_name)()
            for row in rows:
                writer.writerow(row)

    #
    # Gethods to generate self.fake rows
    #

    def manufacturer(self) -> Generator[tuple, None, None]:
        """Returns a list of rows for manufacturer"""
        yield "id", "name", "location", "tax_number"
        for i in range(1, self.count + 1):
            yield self.generate_manufacturer(i)

    def user(self) -> Generator[tuple, None, None]:
        yield "id", "first_name", "last_name", "phone", "password"
        for i in range(1, self.count + 1):
            yield self.generate_user(i)

    def address(self) -> Generator[tuple, None, None]:
        yield "id", "street", "building", "entrance", "intercom", "floor", "apartment"
        for i in range(1, self.count + 1):
            yield self.generate_address(i)

    def comment(self) -> Generator[tuple, None, None]:
        yield "id", "text"
        for i in range(1, self.count + 1):
            yield self.generate_comment(i)

    def electric_vehicle(self) -> Generator[tuple, None, None]:
        yield "id", "type", "mileage", "production_time"
        for i in range(1, self.count + 1):
            yield self.generate_electric_vehicle(i)

    def courier(self) -> Generator[tuple, None, None]:
        yield "id", "user", "vehicle", "passport", "employment_record", "residence_place"
        for i in range(1, self.count + 1):
            yield self.generate_courier(i)

    def client(self) -> Generator[tuple, None, None]:
        yield "id", "user", "individual"
        for i in range(1, self.count + 1):
            yield self.generate_client(i)

    def order(self) -> Generator[tuple, None, None]:
        yield (
            "id",
            "client",
            "courier",
            "create_time",
            "address_from",
            "address_to",
            "weight",
            "comment",
            "delivery_max_time",
            "take_time",
            "deliver_time",
            "delivered",
            "rate",
        )
        for i in range(1, self.count + 1):
            yield self.generate_order(i)

    #
    # Primitive methods to generate 1 row
    #

    def generate_manufacturer(self, i: int) -> tuple[int, str, str, str]:
        id, name, location, tax_number = (
            i,
            self.fake.company(),
            self.fake.address(),
            str(abs(self.fake.pydecimal(15, 0))),
        )
        return id, name, location, tax_number

    def generate_user(self, i: int) -> tuple[int, str, str, str, str]:
        id, first_name, last_name, phone, password = (
            i,
            self.fake.first_name(),
            self.fake.last_name(),
            self.fake.phone_number()[:15],
            self.ph.hash(self.fake.password()),
        )
        return id, first_name, last_name, phone, password

    def generate_address(self, i: int) -> tuple[int, str, str, str, str, str, str]:
        intercom = self.fake.pyint(1, 500)
        id, street, building, entrance, intercom, floor, apartment = (
            i,
            self.fake.street_name(),
            self.fake.building_number(),
            self.fake.pyint(1, 20),
            intercom,
            self.fake.pyint(1, 20),
            intercom,
        )
        return id, street, building, entrance, intercom, floor, apartment

    def generate_comment(self, i: int) -> tuple[int, str]:
        id, text = i, self.fake.text()
        return id, text

    def generate_electric_vehicle(self, i: int) -> tuple[int, int, int, str]:
        id, type, mileage, production_time = (
            i,
            self.fake.pyint(1, 8),  # only 8 rows
            self.fake.pyfloat(4, 3, True),
            f"{self.fake.date_this_decade()} {self.fake.time()}",
        )
        return id, type, mileage, production_time

    def generate_courier(self, i) -> tuple[int, int, int, str, str, str]:
        id, user, vehicle, passport, employment_record, residence_place = (
            i,
            i + 10,
            self.fake.pyint(1, self.count),
            random.choice(courier_passports),
            str(abs(self.fake.pydecimal(20, 0))),
            self.fake.street_address(),
        )
        return id, user, vehicle, passport, employment_record, residence_place

    def generate_client(self, i):
        id, user, individual = i, i, self.fake.pybool()
        return id, user, individual

    def generate_order(self, i):
        (
            id,
            client,
            courier,
            create_time,
            address_from,
            address_to,
            weight,
            comment,
            delivery_max_time,
            take_time,
            deliver_time,
            delivered,
            rate,
        ) = (
            uuid4(),
            self.fake.pyint(1, self.count),
            self.fake.pyint(1, self.count),
            f"{self.fake.date_this_decade()} {self.fake.time()}",
            self.fake.pyint(1, self.count),
            self.fake.pyint(1, self.count),
            self.fake.pyfloat(2, 2, True),
            self.fake.pyint(1, self.count),
            f"{self.fake.pyint(1, 12)} hours",
            f"{self.fake.date_this_decade()} {self.fake.time()}",
            f"{self.fake.date_this_decade()} {self.fake.time()}",
            self.fake.pybool(),
            self.fake.pyint(1, 5),
        )
        return (
            id,
            client,
            courier,
            create_time,
            address_from,
            address_to,
            weight,
            comment,
            delivery_max_time,
            take_time,
            deliver_time,
            delivered,
            rate,
        )


if __name__ == "__main__":
    fire.Fire(Generator)
