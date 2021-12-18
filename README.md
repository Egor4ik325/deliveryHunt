# deliveryHunt

deliveryHunt - express delivery service.

## Security

- Password (argon2 adaptive hashing)
- SQL injection (psycopg3 escape placeholders)
- XSS (Jinja template escape variables)
- Session authentication (Flask secret key encrypted by secret_key)
- CSRF (Python secrets CSRF token + encrypted session)
