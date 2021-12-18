import secrets

from argon2 import PasswordHasher
from flask import Flask, g, redirect, render_template, request, session, url_for
from werkzeug.exceptions import BadRequest, NotFound

import orm

# Secret key is used to encrypt session cookie data (not modifiable for client)
SECRET_KEY = "45e62b268ac88e98d5d4d8687b9a47c08c00c43edd662581724d27f1bc8b5f33"

app = Flask(__name__)
app.secret_key = SECRET_KEY

ph = PasswordHasher()


@app.errorhandler(NotFound)
def handle_not_found(error):
    return render_template("404.html"), 404


app.register_error_handler(404, handle_not_found)


def login_required(func):
    # Page authorization
    def wrapper():
        if not "user" in g:
            raise NotFound

        func()

    return wrapper


@app.before_request
def before():
    # If user is logged-in (user id is set inside cookie)
    if "user_id" in session:
        g.user = orm.users.get(id_=session["user_id"])


@app.after_request
def after(response):
    return response


@app.route("/")
def index():
    return render_template("index.html", user=g.get("user"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in g:
        return redirect(url_for("index"))

    if request.method == "POST":
        phone = request.form.get("phone")
        password = request.form.get("password")

        user = orm.users.get(phone=phone)

        # If user with such phone doesn't exist render errors
        if user is None:
            errors = ["Invalid phone or password."]
            return render_template("login.html", errors=errors)

        # Check password is valid
        if not ph.verify(user.password, password):
            errors = ["Invalid phone or password."]
            return render_template("login.html", errors=errors)

        # Set session cookie
        session["user_id"] = user.id
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id")
    return redirect(url_for("index"))


@app.route("/register")
def register():
    if "user" in g:
        return redirect(url_for("index"))
    return render_template("register.html")


@login_required
@app.route("/orders")
def orders():
    user = g.user
    orders = []
    if user.is_client:
        client = user.client
        orders = orm.orders.list(client=client)
        return render_template("orders.html", user=user, orders=orders)
    elif user.is_courier:
        free_orders = orm.orders.list_free()
        courier = user.courier
        taken_orders = orm.orders.list_taken(courier)
        return render_template(
            "orders.html", user=user, free_orders=free_orders, taken_orders=taken_orders
        )

    raise NotFound


@app.route("/users")
def users():
    return render_template("users.html", user=g.get("user"), users=orm.users.list())


@app.route("/vehicles")
def vehicles():
    return render_template("vehicles.html", user=g.get("user"))


@login_required
@app.route("/orders/<id>")
def order_detail(id: str):
    order = orm.orders.get(id)
    if order is None:
        raise NotFound

    return render_template("order_detail.html", order=order)


@login_required
@app.route("/orders/create")
def order_create():
    if request.method == "POST":
        # try/except
        weight = request.form.get("weight")
        max_delivery_time = request.form.get("max_delivery_time")
        if weight is None or max_delivery_time is None:
            # errors =
            return render_template("orders_create.html")

    return render_template("orders_create.html")


# if __name__ == "__main__":
#     app.run()


@login_required
@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        # Compare csrf tokens (last set for /form page)
        csrf_token = session.get("form_page_csrf_token", None)
        if csrf_token is None:
            return "CSRF token is not set in the session. You didn't requested this form before."

        form_csrf_token = request.form.get("csrf_token")
        if form_csrf_token is None:
            return "This is not real form (it doesn't include set CSRF token)"

        if form_csrf_token != csrf_token:
            return "This is not real form (CSRF token is not the same as in session)"

        return redirect(url_for("done"))

    # Generate random security token for CSRF protection
    csrf_token = secrets.token_hex()

    # Save token in session (for comparing against secure form)
    # Pass token in the template form (to make it unique)
    session["form_page_csrf_token"] = csrf_token
    return render_template("form.html", csrf_token=csrf_token)


@login_required
@app.route("/done")
def done():
    return "You have done very dangerous action!"
