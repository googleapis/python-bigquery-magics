# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""System tests for Jupyter/IPython connector."""

import re

from IPython.testing import globalipapp
from IPython.utils import io
import pandas
import psutil


def test_bigquery_magic():
    globalipapp.start_ipython()
    ip = globalipapp.get_ipython()
    current_process = psutil.Process()
    conn_count_start = len(current_process.net_connections())

    ip.extension_manager.load_extension("bigquery_magics")
    sql = """
        SELECT
            CONCAT(
            'https://stackoverflow.com/questions/',
            CAST(id as STRING)) as url,
            view_count
        FROM `bigquery-public-data.stackoverflow.posts_questions`
        WHERE tags like '%google-bigquery%'
        ORDER BY view_count DESC
        LIMIT 10
    """
    with io.capture_output() as captured:
        result = ip.run_cell_magic("bigquery", "--use_rest_api", sql)

    conn_count_end = len(current_process.net_connections())

    lines = re.split("\n|\r", captured.stdout)
    # Removes blanks & terminal code (result of display clearing)
    updates = list(filter(lambda x: bool(x) and x != "\x1b[2K", lines))
    assert re.match("Executing query with job ID: .*", updates[0])
    assert (re.match("Query executing: .*s", line) for line in updates[1:-1])
    assert isinstance(result, pandas.DataFrame)
    assert len(result) == 10  # verify row count
    assert list(result) == ["url", "view_count"]  # verify column names

    # NOTE: For some reason, the number of open sockets is sometimes one *less*
    # than expected when running system tests on Kokoro, thus using the <= assertion.
    # That's still fine, however, since the sockets are apparently not leaked.
    assert conn_count_end <= conn_count_start  # system resources are released
