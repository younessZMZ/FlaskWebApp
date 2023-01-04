__author__ = "yzemzgui"

import sqlite3

from flask import (Flask, abort, flash, redirect, render_template, request,
                   url_for)
from forms import CourseForm
from markupsafe import escape

app = Flask(__name__)
app.config["SECRET_KEY"] = "3dba5e7ffcad79a69098833e0448bab8970b80f7bf10f5fd"


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), error.code


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), error.code


@app.route("/500")
def error500():
    abort(500)


messages = [
    {"title": "Message One", "content": "Message One Content"},
    {"title": "Message Two", "content": "Message Two Content"},
]


@app.route("/")
def hello():
    return render_template("index.html", messages=messages)


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/comments/")
def comments():
    comments = [
        "This is the first comment.",
        "This is the second comment.",
        "This is the third comment.",
        "This is the fourth comment.",
    ]

    return render_template("comments.html", comments=comments)


@app.route("/messages/<int:idx>")
def message(idx):
    app.logger.info("Building the messages list...")
    messages = ["Message Zero", "Message One", "Message Two"]
    try:
        app.logger.debug("Get message with index: {}".format(idx))
        return render_template("message.html", message=messages[idx])
    except IndexError:
        app.logger.error("Index {} is causing an IndexError".format(idx))
        abort(404)


@app.route("/capitalize/<word>/")
def capitalize(word):
    return "<h1>{}</h1>".format(escape(word.capitalize()))


@app.route("/add/<int:n1>/<int:n2>/")
def add(n1, n2):
    return "<h1>{}</h1>".format(n1 + n2)


@app.route("/users/<int:user_id>/")
def greet_user(user_id):
    users = ["Bob", "Jane", "Adam"]
    try:
        return "<h2>Hi {}</h2>".format(users[user_id])
    except IndexError:
        abort(404)


# setting up forms
@app.route("/create/", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        elif not content:
            flash("Content is required!")
        else:
            messages.append({"title": title, "content": content})
            return redirect(url_for("hello"))
    return render_template("create.html")


# adding forms with WTF-Forms
courses_list = [
    {
        "title": "Python 101",
        "description": "Learn Python basics",
        "price": 34,
        "available": True,
        "level": "Beginner",
    }
]


@app.route("/form", methods=("GET", "POST"))
def form():
    form = CourseForm()
    if form.validate_on_submit():
        courses_list.append(
            {
                "title": form.title.data,
                "description": form.description.data,
                "price": form.price.data,
                "available": form.available.data,
                "level": form.level.data,
            }
        )
        return redirect(url_for("courses"))
    return render_template("form.html", form=form)


@app.route("/courses/")
def courses():
    return render_template("courses.html", courses_list=courses_list)


# connecting and inserting data to sqlite database
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


@app.route("/sqlite")
def index():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM posts").fetchall()
    conn.close()
    return render_template("sqlite_index.html", posts=posts)


@app.route("/sql_create/", methods=("GET", "POST"))
def sql_create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        elif not content:
            flash("Content is required!")
        else:
            conn = get_db_connection()
            conn.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for("index"))
    return render_template("sql_create.html")


@app.route("/<int:id_>/edit/", methods=("GET", "POST"))
def edit(id_):
    post = get_post(id_)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")

        elif not content:
            flash("Content is required!")

        else:
            conn = get_db_connection()
            conn.execute(
                "UPDATE posts SET title = ?, content = ? WHERE id = ?",
                (title, content, id_),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("index"))

    return render_template("edit.html", post=post)


@app.route("/<int:id_>/delete/", methods=("POST",))
def delete(id_):
    post = get_post(id_)
    conn = get_db_connection()
    conn.execute("DELETE FROM posts WHERE id = ?", (id_,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post["title"]))
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
