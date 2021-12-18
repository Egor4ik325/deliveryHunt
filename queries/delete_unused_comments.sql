DELETE FROM
    public.comment
WHERE
    (
        public.comment.id NOT IN(
            SELECT
                public.order.comment
            FROM
                public.order
        )
    ) IS NOT NULL;