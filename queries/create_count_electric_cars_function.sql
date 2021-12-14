CREATE FUNCTION count_electric_cars() RETURNS INTEGER LANGUAGE plpgsql AS $ $ BEGIN RETURN (
    SELECT
        COUNT(*) AS electric_car_count
    FROM
        electric_vehicle
    WHERE
        "type" = 4
);

END;

$ $;

SELECT
    count_electric_cars();