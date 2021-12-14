SELECT
    COUNT(*)
FROM
    "comment"
WHERE
    text ILIKE '%оставьте%'
    OR text ILIKE '%left%';