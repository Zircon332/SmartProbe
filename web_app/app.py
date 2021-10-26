import boto3
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, url_for

load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    return redirect(url_for("view_overview"))

@app.route("/node/")
def view_overview():
    return render_template("overview.html")

@app.route("/node/<node_id>")
def view_node(node_id):
    return render_template("node.html", node_id=node_id)
