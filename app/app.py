from flask import Flask, render_template

from db import get_users

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("index.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/orders")
def orders():
    return render_template("orders.html")


@app.route("/users")
def users():
    users = get_users()
    return render_template("users.html", users=users)


if __name__ == "__main__":
    app.run()
