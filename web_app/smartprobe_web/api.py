import boto3
from boto3.dynamodb.conditions import Key
import functools

from flask import abort, Blueprint, jsonify, render_template, redirect, url_for

bp = Blueprint("api", __name__, url_prefix="/api/node")

@bp.route("/")
def get_nodes():
    table_nodes = boto3.resource("dynamodb").Table("nodes")

    # Retrieve all items in "nodes" table
    res = table_nodes.scan()

    return jsonify(res["Items"])

@bp.route("/<node_id>")
def get_node(node_id):
    table_nodes = boto3.resource("dynamodb").Table("nodes")

    res = table_nodes.get_item(Key={ "id": node_id })

    if "Item" not in res:
        abort(404)

    return res["Item"]

@bp.route("/<node_id>/data")
def get_node_data(node_id):
    table_data = boto3.resource("dynamodb").Table("sensors_data")

    res = table_data.query(
        ScanIndexForward=False,
        KeyConditionExpression=Key("id").eq(node_id))

    return jsonify(res["Items"])

@bp.route("/<node_id>/actions")
def get_node_actions(node_id):
    table_data = boto3.resource("dynamodb").Table("actions")

    res = table_data.query(
        ScanIndexForward=False,
        KeyConditionExpression=Key("id").eq(node_id))

    return jsonify(res["Items"])
