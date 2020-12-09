from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from myblog.auth import login_required
from myblog.db import get_db

from myblog.form import CreateBlogForm

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the blogs, most recent first."""
    db = get_db()
    query_response = db.execute(
        "SELECT p.id, title, body, created, author_id, username, public"
        " FROM blog p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()

    blogs = []
    for row in query_response:
        print('row id: ', row['id'])
        print('row title: ', row['title'])
        print('row public: ', row['public'])

        if g.user:
            if row["author_id"] != g.user["id"] and row['public'] == 0:
                continue
        else:
            if row['public'] == 0:
                continue

        blogs.append(row)

    return render_template("blog/index.html", blogs=blogs)


def get_blog(id, check_author=True, check_public=True):
    """Get a blog and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of blog to get
    :param check_author: require the current user to be the author
    :return: the blog with author information
    :raise 404: if a blog with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    blog = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username, public"
            " FROM blog p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if blog is None:
        abort(404, f"Blog id {id} doesn't exist.")

    if check_author and blog["author_id"] != g.user["id"]:
        abort(403)

    if g.user:
        if check_public and blog["public"] == 0 and blog["author_id"] != g.user["id"]:
            abort(403)
    else:
        if check_public and blog["public"] == 0:
            abort(403)

    return blog


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new blog for the current user."""
    form = CreateBlogForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        body = form.body.data
        public = form.public.data
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO blog (title, body, public, author_id) VALUES (?, ?, ?, ?)",
                (title, body, public, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    elif request.method == "POST" and not form.validate():
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, field_name.capitalize())

    return render_template("blog/create.html", form=form)


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a blog if the current user is the author."""
    if request.method == "GET":
        blog =  get_blog(id)
        form = CreateBlogForm(obj=blog)
    else:
        form = CreateBlogForm(request.form)
    if request.method == "POST":
        title = form.title.data
        body = form.body.data
        public = form.public.data

        blog = get_blog(id)
        if g.user['id'] != blog['author_id']:
            abort(403)

        db = get_db()
        db.execute(
            "UPDATE blog SET title = ?, body = ?, public = ? WHERE id = ?", (title, body, public, id)
        )
        db.commit()
        return redirect(url_for("blog.index"))

    elif request.method == "POST" and not form.validate():
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, field_name.capitalize())

    return render_template("blog/update.html", form=form, blog=blog)


@bp.route("/<int:id>/detail")
def detail(id):
    """Detail a blog if is public."""
    blog = get_blog(id, check_author=False)
    
    return render_template("blog/detail.html", blog=blog)


@bp.route("/<int:id>/delete", methods=("POST", "GET"))
@login_required
def delete(id):
    """Delete a blog.

    Ensures that the blog exists and that the logged in user is the
    author of the blog.
    """
    get_blog(id)
    db = get_db()
    db.execute("DELETE FROM blog WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
