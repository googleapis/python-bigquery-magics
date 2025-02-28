# Copyright 2024 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import atexit
import http.server
import json
import socketserver
import threading
from typing import Dict, List

from networkx.classes import DiGraph
import portpicker
import requests


def convert_graph_data(query_results: Dict[str, Dict[str, str]]):
    """
    Converts graph data to the form expected by the visualization framework.

    Receives graph data as a dictionary, produced by converting the underlying
    DataFrame representing the query results into JSON, then into a
    python dictionary. Converts it into a form expected by the visualization
    framework.

    Args:
        query_results:
            A dictionary with one key/value pair per column. For each column:
            - The key is the name of the column (str)
            - The value is another dictionary with one key/value pair per row.
              Row each row:
              - The key is a string that specifies the integer index of the row
                (e.g. '0', '1', '2')
              - The value is a JSON string containing the result of the query
                for the current row/column. (Note: We only support graph
                visualization for columns of type JSON).
    """
    # Delay spanner imports until this function is called to avoid making
    # # spanner_graphs (and its dependencies) hard requirements for bigquery
    # magics users, who don't need graph visualization.
    #
    # Note that these imports do not need to be in a try/except, as this function
    # does not even get called unless spanner_graphs has already been confirmed
    # to exist upstream.
    from google.cloud.spanner_v1.types import StructType, Type, TypeCode
    from spanner_graphs.conversion import (
        columns_to_native_numpy,
        prepare_data_for_graphing,
    )

    try:
        column_name = None
        column_value = None
        for key, value in query_results.items():
            if column_name is None:
                if not isinstance(key, str):
                    raise ValueError(f"Expected outer key to be str, got {type(key)}")
                if not isinstance(value, dict):
                    raise ValueError(f"Expected outer value to be dict, got {type(value)}")
                column_name = key
                column_value = value
            else:
                # TODO: Implement multi-column support.
                raise ValueError(
                    "Query has multiple columns - graph visualization not supported"
                )
        if column_name is None or column_value is None:
            raise ValueError(
                "query result with no columns is not supported for graph visualization"
            )

        fields: List[StructType.Field] = [
            StructType.Field(name=column_name, type=Type(code=TypeCode.JSON))
        ]
        data = {column_name: []}
        rows = []
        for value_key, value_value in column_value.items():
            if not isinstance(value_key, str):
                raise ValueError(f"Expected inner key to be str, got {type(value_key)}")
            if not isinstance(value_value, str):
                raise ValueError(f"Expected inner value to be str, got {type(value_value)}")
            row_index = int(value_key)
            row_json = json.loads(value_value)

            if row_index != len(data[column_name]):
                raise ValueError(
                    f"Unexpected row index; expected {len(data[column_name])}, got {row_index}"
                )
            data[column_name].append(row_json)
            rows.append([row_json])

        d, ignored_columns = columns_to_native_numpy(data, fields)

        graph: DiGraph = prepare_data_for_graphing(incoming=d, schema_json=None)

        nodes = []
        for node_id, node in graph.nodes(data=True):
            nodes.append(node)

        edges = []
        for from_id, to_id, edge in graph.edges(data=True):
            edges.append(edge)

        return {
            "response": {
                "nodes": nodes,
                "edges": edges,
                "schema": None,
                "rows": rows,
                "query_result": data,
            }
        }
    except Exception as e:
        return {"error": getattr(e, "message", str(e))}


class GraphServer:
    port = portpicker.pick_unused_port()
    host = "http://localhost"
    url = f"{host}:{port}"

    endpoints = {
        "get_ping": "/get_ping",
        "post_ping": "/post_ping",
        "post_query": "/post_query",
    }

    _server = None

    @staticmethod
    def build_route(endpoint):
        return f"{GraphServer.url}{endpoint}"

    @staticmethod
    def start_server():
        class ThreadedTCPServer(socketserver.TCPServer):
            # Allow socket reuse to avoid "Address already in use" errors
            allow_reuse_address = True
            # Daemon threads automatically terminate when the main program exits
            daemon_threads = True

        with ThreadedTCPServer(("", GraphServer.port), GraphServerHandler) as httpd:
            GraphServer._server = httpd
            GraphServer._server.serve_forever()

    @staticmethod
    def init():
        server_thread = threading.Thread(target=GraphServer.start_server)
        server_thread.start()
        return server_thread

    @staticmethod
    def stop_server():
        if GraphServer._server:
            GraphServer._server.shutdown()
            print("BigQuery-magics graph server shutting down...")

    @staticmethod
    def get_ping():
        route = GraphServer.build_route(GraphServer.endpoints["get_ping"])
        response = requests.get(route)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}")
            return False

    @staticmethod
    def post_ping(data):
        route = GraphServer.build_route(GraphServer.endpoints["post_ping"])
        response = requests.post(route, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}")
            return False


class GraphServerHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_json_response(self, data):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_message_response(self, message):
        self.do_json_response({"message": message})

    def do_data_response(self, data):
        self.do_json_response(data)

    def parse_post_data(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")
        return json.loads(post_data)

    def handle_get_ping(self):
        self.do_message_response("pong")

    def handle_post_ping(self):
        data = self.parse_post_data()
        self.do_data_response({"your_request": data})

    def handle_post_query(self):
        data = self.parse_post_data()
        response = convert_graph_data(query_results=json.loads(data["params"]))
        self.do_data_response(response)

    def do_GET(self):
        if self.path == GraphServer.endpoints["get_ping"]:
            self.handle_get_ping()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == GraphServer.endpoints["post_ping"]:
            self.handle_post_ping()
        elif self.path == GraphServer.endpoints["post_query"]:
            self.handle_post_query()


atexit.register(GraphServer.stop_server)
