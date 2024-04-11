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

import google.api_core.client_options as client_options
import google.auth  # type: ignore
import google.cloud.bigquery as bigquery


class Context(object):
    """Storage for objects to be used throughout an IPython notebook session.

    A Context object is initialized when the ``bigquery_magics`` module is imported,
    and can be found at ``bigquery_magics.context``.
    """

    def __init__(self):
        self._credentials = None
        self._project = None
        self._connection = None
        self._default_query_job_config = bigquery.QueryJobConfig()
        self._bigquery_client_options = client_options.ClientOptions()
        self._bqstorage_client_options = client_options.ClientOptions()
        self._progress_bar_type = "tqdm_notebook"

    @property
    def credentials(self):
        """google.auth.credentials.Credentials: Credentials to use for queries
        performed through IPython magics.

        Note:
            These credentials do not need to be explicitly defined if you are
            using Application Default Credentials. If you are not using
            Application Default Credentials, manually construct a
            :class:`google.auth.credentials.Credentials` object and set it as
            the context credentials as demonstrated in the example below. See
            `auth docs`_ for more information on obtaining credentials.

        Example:
            Manually setting the context credentials:

            >>> from google.cloud.bigquery import magics
            >>> from google.oauth2 import service_account
            >>> credentials = (service_account
            ...     .Credentials.from_service_account_file(
            ...         '/path/to/key.json'))
            >>> bigquery_magics.context.credentials = credentials


        .. _auth docs: http://google-auth.readthedocs.io
            /en/latest/user-guide.html#obtaining-credentials
        """
        if self._credentials is None:
            self._credentials, _ = google.auth.default()
        return self._credentials

    @credentials.setter
    def credentials(self, value):
        self._credentials = value

    @property
    def project(self):
        """str: Default project to use for queries performed through IPython
        magics.

        Note:
            The project does not need to be explicitly defined if you have an
            environment default project set. If you do not have a default
            project set in your environment, manually assign the project as
            demonstrated in the example below.

        Example:
            Manually setting the context project:

            >>> from google.cloud.bigquery import magics
            >>> bigquery_magics.context.project = 'my-project'
        """
        if self._project is None:
            _, self._project = google.auth.default()
        return self._project

    @project.setter
    def project(self, value):
        self._project = value

    @property
    def bigquery_client_options(self):
        """google.api_core.client_options.ClientOptions: client options to be
        used through IPython magics.

        Note::
            The client options do not need to be explicitly defined if no
            special network connections are required. Normally you would be
            using the https://bigquery.googleapis.com/ end point.

        Example:
            Manually setting the endpoint:

            >>> from google.cloud.bigquery import magics
            >>> client_options = {}
            >>> client_options['api_endpoint'] = "https://some.special.url"
            >>> bigquery_magics.context.bigquery_client_options = client_options
        """
        return self._bigquery_client_options

    @bigquery_client_options.setter
    def bigquery_client_options(self, value):
        self._bigquery_client_options = value

    @property
    def bqstorage_client_options(self):
        """google.api_core.client_options.ClientOptions: client options to be
        used through IPython magics for the storage client.

        Note::
            The client options do not need to be explicitly defined if no
            special network connections are required. Normally you would be
            using the https://bigquerystorage.googleapis.com/ end point.

        Example:
            Manually setting the endpoint:

            >>> from google.cloud.bigquery import magics
            >>> client_options = {}
            >>> client_options['api_endpoint'] = "https://some.special.url"
            >>> bigquery_magics.context.bqstorage_client_options = client_options
        """
        return self._bqstorage_client_options

    @bqstorage_client_options.setter
    def bqstorage_client_options(self, value):
        self._bqstorage_client_options = value

    @property
    def default_query_job_config(self):
        """google.cloud.bigquery.job.QueryJobConfig: Default job
        configuration for queries.

        The context's :class:`~google.cloud.bigquery.job.QueryJobConfig` is
        used for queries. Some properties can be overridden with arguments to
        the magics.

        Example:
            Manually setting the default value for ``maximum_bytes_billed``
            to 100 MB:

            >>> from google.cloud.bigquery import magics
            >>> bigquery_magics.context.default_query_job_config.maximum_bytes_billed = 100000000
        """
        return self._default_query_job_config

    @default_query_job_config.setter
    def default_query_job_config(self, value):
        self._default_query_job_config = value

    @property
    def progress_bar_type(self):
        """str: Default progress bar type to use to display progress bar while
        executing queries through IPython magics.

        Note::
            Install the ``tqdm`` package to use this feature.

        Example:
            Manually setting the progress_bar_type:

            >>> from google.cloud.bigquery import magics
            >>> bigquery_magics.context.progress_bar_type = "tqdm_notebook"
        """
        return self._progress_bar_type

    @progress_bar_type.setter
    def progress_bar_type(self, value):
        self._progress_bar_type = value


context = Context()
