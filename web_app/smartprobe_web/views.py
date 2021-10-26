import functools

from flask import Blueprint, render_template, redirect, url_for

bp = Blueprint("views", __name__)

@bp.route("/")
def index():
    return redirect(url_for("views.overview"))

@bp.route("/node/")
def overview():
    return render_template("overview.html")

@bp.route("/node/<node_id>")
def node(node_id):
    return render_template("node.html", node_id=node_id)
