from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db


views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


@views.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        post = request.form.get("post")
        if not post:
            flash("Post cannot be empty", category="error")
        else:
            p = Post()
            p.post = post
            p.author = current_user.id
            db.session.add(p)
            db.session.commit()
            flash("Post created", category="success")
            return redirect(url_for("views.home"))
    return render_template("create-post.html", user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        flash("Post does not exist.", category="error")
    elif current_user.id != post.author:
        flash("You do not have permission to delete this post.", category="error")
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted.", category="success")
    return redirect(url_for("views.home"))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("No user with that username exists", category="error")
        return redirect(url_for("view.home"))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)


@views.route("/create-comment/<post_id>", methods=["POST"])
@login_required
def create_comment(post_id):
    comment = request.form.get("comment")
    if not comment:
        flash("Comment cannot be empty.", category="error")
    else:
        post = Post.query.filter_by(id=post_id).first()
        if not post:
            flash("Post does not exist.", category="error")
        else:
            c = Comment()
            c.comment = comment
            c.author = current_user.id
            c.post_id = post_id
            db.session.add(c)
            db.session.commit()
    return redirect(url_for("views.home"))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash("Comment does not exist.", category="error")
    elif current_user.id != comment.author or current_user.id != comment.post.author:
        flash("You don't have permission to delete this comment.", category="error")
    else:
        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted.", category="success")
    return redirect(url_for("views.home"))


@views.route("/like-post/<post_id>", methods=["GET"])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if not post:
        return flash("Post does not exist.", category="error")
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like()
        like.author = current_user.id
        like.post_id = post_id
        db.session.add(like)
        db.session.commit()
    return redirect(url_for("views.home"))
