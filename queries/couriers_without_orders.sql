SELECT
    first_name,
    phone
FROM
    courier
    INNER JOIN "user" ON courier.user = "user".id
WHERE
    courier."id" NOT IN (
        SELECT
            courier
        FROM
            "order"
    )