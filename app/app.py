from argon2 import PasswordHasher
from flask import Flask, redirect, render_template, request, session, url_for

import orm

# Secret key is used to encrypt session cookie data (not modifiable for client)
SECRET_KEY = "45e62b268ac88e98d5d4d8687b9a47c08c00c43edd662581724d27f1bc8b5f33"

app = Flask(__name__)
app.secret_key = SECRET_KEY

ph = PasswordHasher()


@app.route("/")
def index():
    # If user is logged-in (user id is set inside cookie)
    if "user_id" in session:
        user = orm.users.get(id_=session["user_id"])

        if user is not None:
            return render_template("index.html", user=user)

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
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
    return render_template("register.html")


@app.route("/orders")
def orders():
    return render_template("orders.html")


@app.route("/users")
def users():
    return render_template("users.html", users=orm.users.list())


# if __name__ == "__main__":
#     app.run()
