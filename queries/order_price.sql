SELECT
    (
        (from_address."floor" :: integer * 20) + (to_address."floor" :: integer * 20) + (
            EXTRACT (
                HOUR
                FROM
                    "order".max_delivery_time
            ) * 400
        )
    ) * (1 - 0.8 * (NOT client.individual) :: integer) + (50 * ("order".rate = 1) :: integer)
FROM
    "order"
    INNER JOIN address AS from_address ON "order".address_from = from_address.id
    INNER JOIN address AS to_address ON "order".address_to = to_address.id
    INNER JOIN client ON "order".client = client.id
WHERE
    "order".id = '39cc0da1-b7ec-4f50-b72e-58baaa4dcc59';