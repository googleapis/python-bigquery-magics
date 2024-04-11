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

import io
import os

import setuptools

# Package metadata.

name = "bigquery-magics"
description = "Google BigQuery magics for Jupyter and IPython"

# Should be one of:
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'``
release_status = "Development Status :: 4 - Beta"
dependencies = [
    "db-dtypes>=0.3.0,<2.0.0dev",
    "google-cloud-bigquery >= 3.13.0, <4.0.0dev",
    "ipywidgets>=7.7.1",
    "ipython>=7.23.1",
    "ipykernel>=6.0.0",
    "packaging >= 20.0.0",
    "pandas>=1.1.0",
    "pyarrow >= 3.0.0",
    "tqdm >= 4.7.4, <5.0.0dev",
]
extras = {
    # bqstorage had a period where it was a required dependency, and has been
    # moved back to optional due to bloat.  See
    # https://github.com/googleapis/python-bigquery/issues/1196 for more background.
    "bqstorage": [
        "google-cloud-bigquery-storage >= 2.6.0, <3.0.0dev",
        # Due to an issue in pip's dependency resolver, the `grpc` extra is not
        # installed, even though `google-cloud-bigquery-storage` specifies it
        # as `google-api-core[grpc]`. We thus need to explicitly specify it here.
        # See: https://github.com/googleapis/python-bigquery/issues/83 The
        # grpc.Channel.close() method isn't added until 1.32.0.
        # https://github.com/grpc/grpc/pull/15254
        "grpcio >= 1.47.0, < 2.0dev",
        "grpcio >= 1.49.1, < 2.0dev; python_version>='3.11'",
    ],
}

all_extras = []

for extra in extras:
    all_extras.extend(extras[extra])

extras["all"] = all_extras

# Setup boilerplate below this line.

package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, "README.rst")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

version = {}
with open(os.path.join(package_root, "bigquery_magics/version.py")) as fp:
    exec(fp.read(), version)
version = version["__version__"]

# Only include packages under the 'bigquery_magics' namespace. Do not include tests,
# benchmarks, etc.
packages = [
    package
    for package in setuptools.find_namespace_packages()
    if package.startswith("bigquery_magics")
]

setuptools.setup(
    name=name,
    version=version,
    description=description,
    long_description=readme,
    author="Google LLC",
    author_email="googleapis-packages@google.com",
    license="Apache 2.0",
    url="https://github.com/googleapis/python-bigquery-magics",
    classifiers=[
        release_status,
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Internet",
    ],
    platforms="Posix; MacOS X; Windows",
    packages=packages,
    install_requires=dependencies,
    extras_require=extras,
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
)
