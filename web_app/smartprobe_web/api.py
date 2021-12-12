import boto3
from boto3.dynamodb.conditions import Key
from flask import abort, Blueprint, jsonify, render_template, redirect, url_for
import functools
import json

bp = Blueprint("api", __name__, url_prefix="/api/node")

@bp.route("/")
def get_nodes():
    table_nodes = boto3.resource("dynamodb").Table("SmartProbeNodes")

    # Retrieve all items in "nodes" table
    res = table_nodes.scan()

    # Deserialize because values are saved as string in DynamoDB for some reason
    for item in res["Items"]:
        if type(item["sensors"]) is str:
            item["sensors"] = json.loads(item["sensors"])

        if type(item["actions"]) is str:
            item["actions"] = json.loads(item["actions"])

    return jsonify(res["Items"])

@bp.route("/<node_id>")
def get_node(node_id):
    table_nodes = boto3.resource("dynamodb").Table("SmartProbeNodes")

    res = table_nodes.get_item(Key={ "id": node_id })

    if "Item" not in res:
        abort(404)

    # Deserialize because values are saved as string in DynamoDB for some reason
    item = res["Item"]
    if type(item["sensors"]) is str:
        item["sensors"] = json.loads(item["sensors"])

    if type(item["actions"]) is str:
        item["actions"] = json.loads(item["actions"])

    return item

@bp.route("/<node_id>/data")
def get_node_data(node_id):
    table_data = boto3.resource("dynamodb").Table("SmartProbeSensorsData")

    res = table_data.query(
        ScanIndexForward=False,
        KeyConditionExpression=Key("id").eq(node_id))

    return jsonify(res["Items"])

@bp.route("/<node_id>/actions")
def get_node_actions(node_id):
    table_data = boto3.resource("dynamodb").Table("SmartProbeActions")

    res = table_data.query(
        ScanIndexForward=False,
        KeyConditionExpression=Key("id").eq(node_id))

    return jsonify(res["Items"])
