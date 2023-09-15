"""
Copyright (c) 2022, Oracle and/or its affiliates.
Copyright (c) 2020, Vitor Avancini

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""

"""The setup script."""
import sys
from setuptools import setup

try:
    from setuptools import find_namespace_packages
except ImportError:
    # the user has a downlevel version of setuptools.
    print("Error: dbt requires setuptools v40.1.0 or higher.")
    print('Please upgrade setuptools with "pip install --upgrade setuptools" ' "and try again")
    sys.exit(1)


# lockstep with dbt-core which requires Python > 3.8
if sys.version_info < (3, 8):
    print("Error: dbt-oracle does not support this version of Python.")
    print("Please upgrade to Python 3.8 or higher.")
    sys.exit(1)


with open('README.md') as readme_file:
    readme = readme_file.read()


requirements = [
        "dbt-core~=1.6",
        "cx_Oracle==8.3.0",
        "oracledb==1.4.1"
]

test_requirements = [
    "dbt-tests-adapter~=1.6",
    "pytest"
]

project_urls = {
    'Documentation': 'https://docs.getdbt.com/reference/warehouse-profiles/oracle-profile',
    'Source': 'https://github.com/oracle/dbt-oracle',
    'Bug Tracker': 'https://github.com/oracle/dbt-oracle/issues',
    'CI': 'https://github.com/oracle/dbt-oracle/actions',
    "Release Notes": "https://github.com/oracle/dbt-oracle/releases"
}

url = 'https://github.com/oracle/dbt-oracle'

VERSION = '1.6.0'
setup(
    author="Oracle",
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    description="dbt (data build tool) adapter for the Oracle database",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='Oracle dbt',
    name='dbt-oracle',
    packages=find_namespace_packages(include=["dbt", "dbt.*"]),
    test_suite='tests',
    tests_require=test_requirements,
    scripts=['bin/create-pem-from-p12'],
    url=url,
    project_urls=project_urls,
    version=VERSION,
    zip_safe=False
)
