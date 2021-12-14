from flask import Flask, render_template

from db import get_users

app = Flask(__name__)


@app.route("/")
def hello():
    users = get_users()
    return render_template("users.html", users=users)


if __name__ == "__main__":
    app.run()
