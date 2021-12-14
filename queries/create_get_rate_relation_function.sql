CREATE
OR REPLACE FUNCTION get_rate_relation() RETURNS REAL LANGUAGE plpgsql AS $ $ DECLARE rate_count INTEGER;

positive_count INTEGER;

negative_count INTEGER;

BEGIN
SELECT
    COUNT(*) INTO rate_count
FROM
    "order";

SELECT
    COUNT(*) INTO positive_count
FROM
    "order"
WHERE
    rate BETWEEN 3
    AND 5;

SELECT
    rate_count - positive_count INTO negative_count;

IF positive_count >= negative_count THEN RETURN positive_count :: real / negative_count :: real;

ELSE RETURN -(negative_count :: real / positive_count :: real);

END IF;

END;

$ $