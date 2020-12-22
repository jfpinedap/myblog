from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.exceptions import abort

from myblog.auth import login_required
from myblog.db import get_db

from myblog.form import (
    CreateBlogForm, CreateCommentForm, DeleteBlogForm, DeleteCommentForm
)

bp = Blueprint("blog", __name__)

@bp.route("/", methods=("GET",))
def index():
    """Show all the blogs, most recent first."""
    search_val = request.args.get('search')

    db = get_db()
    if search_val:
        print('search_val = ', search_val)
        search_val_whatever = str('%' + search_val + '%')
        query_response = db.execute(
            " SELECT b.id, title, body, updated, author_id, username, public"
            " FROM blog b INNER JOIN user u ON b.author_id = u.id"
            " WHERE "
            "     b.title LIKE ? ESCAPE \'\\\'"
            "   OR "
            "     b.body LIKE ? ESCAPE \'\\\'"
            " ORDER BY updated DESC",
            (search_val_whatever, search_val_whatever),
        ).fetchall()
    else:
        print('search_val = ', search_val)
        query_response = db.execute(
            " SELECT b.id, title, body, updated, author_id, username, public"
            " FROM blog b JOIN user u ON b.author_id = u.id"
            " ORDER BY updated DESC"
        ).fetchall()

    blogs = []
    for row in query_response:
        if g.user:
            if row["author_id"] != g.user["id"] and row['public'] == 0:
                continue
        else:
            if row['public'] == 0:
                continue

        blogs.append(row)

    return render_template("blog/index.html", blogs=blogs, search=search_val)


def get_blog(blog_id, check_author=True, check_public=True):
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
            "SELECT p.id, title, body, updated, author_id, username, public"
            " FROM blog p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (blog_id,),
        )
        .fetchone()
    )

    if blog is None:
        abort(404, f"Blog id {blog_id} doesn't exist.")

    if check_author and blog["author_id"] != g.user["id"]:
        abort(403)

    if g.user:
        if check_public and blog["public"] == 0 and blog["author_id"] != g.user["id"]:
            abort(403)
    else:
        if check_public and blog["public"] == 0:
            abort(403)

    return blog


def get_comment(comment_id, check_author=True):
    """Get a blog and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of blog to get
    :param check_author: require the current user to be the author
    :return: the blog with author information
    :raise 404: if a blog with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    comment = (
        get_db()
        .execute(
            " SELECT c.id, c.text, c.updated, c.author_id"
            " FROM comment c JOIN user u ON c.author_id = u.id"
            " WHERE c.id = ?",
            (comment_id,),
        )
        .fetchone()
    )

    if comment is None:
        abort(404, f"Blog id {comment_id} doesn't exist.")

    if check_author and comment["author_id"] != g.user["id"]:
        abort(403)

    return comment


def get_comments(blog_id):
    """
    Get comments from a blog.
    """
    comments = (
        get_db()
        .execute(
            " SELECT DISTINCT c.id, c.text, c.created, c.author_id"
            " FROM blog b JOIN comment c ON c.blog_id = b.id"
            " WHERE b.id = ?",
            (blog_id,),
        )
        .fetchall()
    )

    return comments


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new blog for the current user."""
    form = CreateBlogForm(request.form, meta={'csrf_context': session})
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


@bp.route("/<int:blog_id>/update", methods=("GET", "POST"))
@login_required
def update(blog_id):
    """Update a blog if the current user is the author."""
    if request.method == "GET":
        blog =  get_blog(blog_id)
        form = CreateBlogForm(obj=blog, meta={'csrf_context': session})
    else:
        form = CreateBlogForm(request.form, meta={'csrf_context': session})
    if request.method == "POST":
        title = form.title.data
        body = form.body.data
        public = form.public.data

        blog = get_blog(blog_id)
        if g.user['id'] != blog['author_id']:
            abort(403)

        db = get_db()
        db.execute(
            "UPDATE blog SET title = ?, body = ?, public = ?, updated = CURRENT_TIMESTAMP WHERE id = ?", (title, body, public, blog_id)
        )
        db.commit()
        return redirect(url_for("blog.index"))

    elif request.method == "POST" and not form.validate():
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, field_name.capitalize())

    return render_template("blog/update.html", form=form, blog=blog)


@bp.route("/<int:blog_id>/comment", methods=("POST",))
@login_required
def comment(blog_id):
    form = CreateCommentForm(request.form, meta={'csrf_context': session})
    if request.method == "POST":
        text = form.text.data

        db = get_db()
        db.execute(
            "INSERT INTO comment (text, author_id, blog_id) VALUES (?, ?, ?)",
            (text, g.user["id"], blog_id),
        )
        db.commit()
        return redirect(url_for("blog.detail", blog_id=blog_id))

    elif request.method == "POST" and not form.validate():
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, field_name.capitalize())


@bp.route("/<int:blog_id>/detail", methods=("GET",))
def detail(blog_id):
    """Detail a blog if is public."""
    blog = get_blog(blog_id, check_author=False)
    comments = get_comments(blog_id=blog_id)
    form = CreateCommentForm(request.form, meta={'csrf_context': session})
    
    return render_template("blog/detail.html", comments=comments, blog=blog, form=form)


@bp.route("/<int:blog_id>/delete", methods=("GET", "POST"))
@login_required
def delete(blog_id):
    """Delete a blog.

    Ensures that the blog exists and that the logged in user is the
    author of the blog.
    """
    form = DeleteBlogForm(request.form, meta={'csrf_context': session})
    if request.method == "POST" and form.validate():
        get_blog(blog_id)
        db = get_db()
        db.execute("DELETE FROM blog WHERE id = ?", (blog_id,))
        db.commit()
        return redirect(url_for("blog.index"))
    
    return render_template("blog/delete_blog.html", form=form, blog=get_blog(blog_id))


@bp.route("/<int:comment_id>/comment_delete", methods=("GET", "POST"))
@login_required
def comment_delete(comment_id):
    """Delete a comment.

    Ensures that the comment exists and that the logged in user is the
    author of the comment.
    """
    form = DeleteCommentForm(request.form, meta={'csrf_context': session})
    if request.method == "POST" and form.validate():
        get_comment(comment_id)
        db = get_db()
        db.execute("DELETE FROM comment WHERE id = ?", (comment_id,))
        db.commit()
        return redirect(url_for("blog.detail", blog_id=request.args.get('blog_id')))

    context = {
        'comment': get_comment(comment_id)["text"],
        'blog_id': request.args.get('blog_id')
    }

    return render_template("blog/delete_comment.html", form=form, context=context)
