# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import unittest

import pytest

try:
    import spanner_graphs.graph_visualization as graph_visualization
except ImportError:
    graph_visualization = None

from bigquery_magics.graph_server import GraphServer, convert_graph_data

alex_properties = {
    "birthday": "1991-12-21T08:00:00Z",
    "id": 1,
    "city": "Adelaide",
    "country": "Australia",
    "name": "Alex",
}

alex_account_properties = {
    "create_time": "2020-01-10T14:22:20.222Z",
    "id": 7,
    "is_blocked": False,
    "nick_name": "Vacation Fund",
}

alex_owns_account_edge_properites = {
    "account_id": 7,
    "create_time": "2020-01-10T14:22:20.222Z",
    "id": 1,
}

row_alex_owns_account = [
    {
        "identifier": "mUZpbkdyYXBoLlBlcnNvbgB4kQI=",
        "kind": "node",
        "labels": ["Person"],
        "properties": alex_properties,
    },
    {
        "destination_node_identifier": "mUZpbkdyYXBoLkFjY291bnQAeJEO",
        "identifier": "mUZpbkdyYXBoLlBlcnNvbk93bkFjY291bnQAeJECkQ6ZRmluR3JhcGguUGVyc29uAHiRAplGaW5HcmFwaC5BY2NvdW50AHiRDg==",
        "kind": "edge",
        "labels": ["Owns"],
        "properties": alex_owns_account_edge_properites,
        "source_node_identifier": "mUZpbkdyYXBoLlBlcnNvbgB4kQI=",
    },
    {
        "identifier": "mUZpbkdyYXBoLkFjY291bnQAeJEO",
        "kind": "node",
        "labels": ["Account"],
        "properties": alex_account_properties,
    },
]

lee_properties = {
    "birthday": "1986-12-07T08:00:00Z",
    "city": "Kollam",
    "country": "India",
    "id": 3,
    "name": "Lee",
}

lee_account_properties = {
    "create_time": "2020-01-28T01:55:09.206Z",
    "id": 16,
    "is_blocked": True,
    "nick_name": "Vacation Fund",
}

lee_owns_account_edge_properties = {
    "account_id": 16,
    "create_time": "2020-02-18T13:44:20.655Z",
    "id": 3,
}

row_lee_owns_account = [
    {
        "identifier": "mUZpbkdyYXBoLlBlcnNvbgB4kQY=",
        "kind": "node",
        "labels": ["Person"],
        "properties": lee_properties,
    },
    {
        "destination_node_identifier": "mUZpbkdyYXBoLkFjY291bnQAeJEg",
        "identifier": "mUZpbkdyYXBoLlBlcnNvbk93bkFjY291bnQAeJEGkSCZRmluR3JhcGguUGVyc29uAHiRBplGaW5HcmFwaC5BY2NvdW50AHiRIA==",
        "kind": "edge",
        "labels": ["Owns"],
        "properties": lee_owns_account_edge_properties,
        "source_node_identifier": "mUZpbkdyYXBoLlBlcnNvbgB4kQY=",
    },
    {
        "identifier": "mUZpbkdyYXBoLkFjY291bnQAeJEg",
        "kind": "node",
        "labels": ["Account"],
        "properties": lee_account_properties,
    },
]


def _validate_nodes_and_edges(result):
    for edge in result["response"]["edges"]:
        assert "id" in edge
        assert edge["label"] == "Owns"
        assert "source" in edge
        assert "target" in edge
        assert "properties" in edge

    for node in result["response"]["nodes"]:
        assert "id" in node
        assert "key_property_names" in node
        assert node["label"] in ("Account", "Person")
        assert "properties" in node
        assert "value" in node


@pytest.mark.skipif(
    graph_visualization is None, reason="Requires `spanner-graph-notebook`"
)
def test_convert_one_column_no_rows():
    result = convert_graph_data({"result": {}})
    assert result == {
        "response": {
            "edges": [],
            "nodes": [],
            "query_result": {"result": []},
            "rows": [],
            "schema": None,
        }
    }


@pytest.mark.skipif(
    graph_visualization is None, reason="Requires `spanner-graph-notebook`"
)
def test_convert_one_column_one_row_one_column():
    result = convert_graph_data(
        {
            "result": {
                "0": json.dumps(row_alex_owns_account),
            }
        }
    )

    assert len(result["response"]["nodes"]) == 2
    assert len(result["response"]["edges"]) == 1

    _validate_nodes_and_edges(result)

    assert result["response"]["query_result"] == {"result": [row_alex_owns_account]}
    assert result["response"]["rows"] == [[row_alex_owns_account]]
    assert result["response"]["schema"] is None


@pytest.mark.skipif(
    graph_visualization is None, reason="Requires `spanner-graph-notebook`"
)
def test_convert_one_column_two_rows():
    result = convert_graph_data(
        {
            "result": {
                "0": json.dumps(row_alex_owns_account),
                "1": json.dumps(row_lee_owns_account),
            }
        }
    )

    assert len(result["response"]["nodes"]) == 4
    assert len(result["response"]["edges"]) == 2

    _validate_nodes_and_edges(result)

    assert result["response"]["query_result"] == {
        "result": [row_alex_owns_account, row_lee_owns_account]
    }
    assert result["response"]["rows"] == [
        [row_alex_owns_account],
        [row_lee_owns_account],
    ]
    assert result["response"]["schema"] is None


@pytest.mark.skipif(
    graph_visualization is None, reason="Requires `spanner-graph-notebook`"
)
def test_convert_nongraph_json():
    # If we have valid json that doesn't represent a graph, we don't expect to get nodes and edges,
    # but we should at least have row data, allowing the tabular view to work.
    result = convert_graph_data(
        {
            "result": {
                "0": json.dumps({"foo": 1, "bar": 2}),
            }
        }
    )

    assert len(result["response"]["nodes"]) == 0
    assert len(result["response"]["edges"]) == 0

    assert result["response"]["query_result"] == {"result": [{"foo": 1, "bar": 2}]}
    assert result["response"]["rows"] == [[{"foo": 1, "bar": 2}]]
    assert result["response"]["schema"] is None


@pytest.mark.skipif(
    graph_visualization is None, reason="Requires `spanner-graph-notebook`"
)
def test_convert_outer_key_not_string():
    result = convert_graph_data(
            {
                0: {
                    '0': json.dumps({"foo": 1, "bar": 2}),
                }
            })
    assert result == {"error": "Expected outer key to be str, got <class 'int'>"}


@pytest.mark.skipif(
    graph_visualization is None, reason="Requires `spanner-graph-notebook`"
)
def test_convert_outer_value_not_dict():
    result = convert_graph_data(
            {
                'result': 0
            })
    assert result == {"error": "Expected outer value to be dict, got <class 'int'>"}


@pytest.mark.skipif(
    graph_visualization is None, reason="Requires `spanner-graph-notebook`"
)
def test_convert_inner_key_not_string():
    result = convert_graph_data(
            {
                'result': {
                    0: json.dumps({"foo": 1, "bar": 2}),
                }
            })
    assert result == {"error": "Expected inner key to be str, got <class 'int'>"}


@pytest.mark.skipif(
    graph_visualization is None, reason="Requires `spanner-graph-notebook`"
)
def test_convert_inner_value_not_string():
    result = convert_graph_data(
            {
                'result': {
                    '0': 1,
                }
            })
    assert result == {"error": "Expected inner value to be str, got <class 'int'>"}


@pytest.mark.skipif(
    graph_visualization is None, reason="Requires `spanner-graph-notebook`"
)
def test_convert_one_column_one_row_two_columns():
    result = convert_graph_data(
        {
            "result1": {
                "0": json.dumps(row_alex_owns_account),
            },
            "result2": {
                "0": json.dumps(row_alex_owns_account),
            }

        }
    )
    assert result == {"error": "Query has multiple columns - graph visualization not supported"}


@pytest.mark.skipif(
    graph_visualization is None, reason="Requires `spanner-graph-notebook`"
)
def test_convert_empty_dict():
    result = convert_graph_data({})
    assert result == {"error": "query result with no columns is not supported for graph visualization"}


class TestGraphServer(unittest.TestCase):
    def setUp(self):
        self.server_thread = GraphServer.init()

    def tearDown(self):
        GraphServer.stop_server()  # Stop the server after each test
        self.server_thread.join()  # Wait for the thread to finish

    def test_ping(self):
        self.assertTrue(self.server_thread.is_alive())

        response = GraphServer.get_ping()
        self.assertEqual(response, {"message": "pong"})

        request = {"data": "ping"}
        response = GraphServer.post_ping(request)
        self.assertEqual(response, {"your_request": request})
