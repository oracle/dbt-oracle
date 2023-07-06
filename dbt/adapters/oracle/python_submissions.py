"""
Copyright (c) 2023, Oracle and/or its affiliates.

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
import datetime
import http
import json
from typing import Dict

import requests
import time

import dbt.exceptions
from dbt.adapters.oracle import OracleAdapterCredentials
from dbt.events import AdapterLogger
from dbt.ui import red, green

# ADB-S OML Rest API minimum timeout is 1800 seconds
DEFAULT_TIMEOUT_IN_SECONDS = 1800
DEFAULT_DELAY_BETWEEN_POLL_IN_SECONDS = 2

OMLUSERS_OAUTH_API = "/omlusers/api/oauth2/v1/token"
OML_DO_EVAL_API = "/oml/api/py-scripts/v1/do-eval/{script_name}"

logger = AdapterLogger("oracle")


class OracleOML4PYClient:

    def __init__(self, oml_cloud_service_url, username, password):
        self.base_url = oml_cloud_service_url
        self._username = username
        self._password = password
        self.token = None
        self.token_expires_at = None
        self.token_url = self.base_url + OMLUSERS_OAUTH_API
        self._session = requests.Session()

    @property
    def session(self):
        return self._session

    def get_token(self):
        """Get access_token or refresh_token"""
        # If access token is about to expire then refresh the token
        if self.token_expires_at and self.token_expires_at - datetime.datetime.utcnow() < datetime.timedelta(minutes=1):
            return self._get_token(grant_type="refresh_token")
        elif self.token:  # Token is valid
            return self.token
        else:  # Generate a new token
            return self._get_token(grant_type="password")

    def _get_token(self, grant_type="password"):
        """Gets access_token or refresh_token using /broker/pdbcs/private/v1/token"""
        data = {"grant_type": grant_type}
        if grant_type == "password":
            data["username"] = self._username
            data["password"] = self._password
        else:
            data["token"] = self.token

        r = self.session.post(
            url=self.token_url,
            json=data,
            headers={
                "Accept": "application/json",
                "Content-type": "application/json",
            },
        )
        r.raise_for_status()
        response = r.json()
        self.token = response["accessToken"]
        self.token_expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=response["expiresIn"])
        return self.token

    @property
    def default_headers(self):
        """Default headers added to every request"""
        return {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.get_token()}",
        }

    def request(self, method: str, path: str,
                raise_for_status: bool = False,
                **kwargs) -> requests.Response:
        """
        Description:
            Perform a desired action (GET, PUT, POST) on a certain resource

        Args:
            method (str) -> HTTP verb like GET, PUT, POST, etc
            path (str) -> path to the resource e.g. /job/{job_id}
            raise_for_status (bool) -> True if HTTPError should be raised in case of an error else False

        Returns:
            object of type request.Response

        Raises:
            requests.HTTPError() in case of en error, if raise_for_status is True

        """
        url = path if path.startswith(self.base_url) else self.base_url + path
        self.session.headers.update(self.default_headers)
        r = self.session.request(method=method, url=url, **kwargs)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            if raise_for_status:
                raise
        return r


class OracleADBSPythonJob:
    """Callable to submit Python Script to ADB-S

    """

    def __init__(self,
                 parsed_model: Dict,
                 credential: OracleAdapterCredentials) -> None:
        self.identifier = parsed_model["alias"]
        self.py_q_script_name = f"{self.identifier}_dbt_py_script"
        self.conda_env_name = parsed_model["config"].get("conda_env_name")
        self.timeout = parsed_model["config"].get("timeout", DEFAULT_TIMEOUT_IN_SECONDS)
        self.async_flag = parsed_model["config"].get("async_flag", False)
        self.service = parsed_model["config"].get("service", "HIGH")
        self.oml4py_client = OracleOML4PYClient(oml_cloud_service_url=credential.oml_cloud_service_url,
                                                username=credential.user,
                                                password=credential.password)

    def schedule_async_job_and_wait_for_completion(self, data):
        logger.info(f"Running Python aysnc job using {data}")
        try:
            r = self.oml4py_client.request(method="POST",
                                           path=OML_DO_EVAL_API.format(script_name=self.py_q_script_name),
                                           data=json.dumps(data),
                                           raise_for_status=False)
            if r.status_code in (http.HTTPStatus.BAD_REQUEST, http.HTTPStatus.INTERNAL_SERVER_ERROR):
                logger.error(red(r.json()))
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(red(f"Error {e} scheduling async Python job for model {self.identifier}"))
            raise dbt.exceptions.DbtRuntimeError(f"Error scheduling Python model {self.identifier}")

        job_location = r.headers["location"]
        logger.info(f"Started async job {job_location}")
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            logger.debug(f"Checking Job status for : {job_location}")
            try:
                job_status = self.oml4py_client.request(method="GET",
                                                        path=job_location,
                                                        raise_for_status=False)
                job_status_code = job_status.status_code
                logger.debug(f"Job status code is: {job_status_code}")
                if job_status_code == http.HTTPStatus.FOUND:
                    logger.info(green(f"Job {job_location} completed"))
                    job_result = self.oml4py_client.request(method="GET",
                                                            path=f"{job_location}/result",
                                                            raise_for_status=False)
                    job_result_json = job_result.json()
                    if 'errorMessage' in job_result_json:
                        logger.error(red(f"FAILURE - Python model {self.identifier} Job failure is: {job_result_json}"))
                        raise dbt.exceptions.DbtRuntimeError(f"Error running Python model {self.identifier}")
                    job_result.raise_for_status()
                    logger.info(green(f"SUCCESS - Python model {self.identifier} Job result is: {job_result_json}"))
                    return
                elif job_status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR:
                    logger.error(red(f"FAILURE - Job status is: {job_status.json()}"))
                    raise dbt.exceptions.DbtRuntimeError(f"Error running Python model {self.identifier}")
                else:
                    logger.debug(f"Python model {self.identifier} job status is: {job_status.json()}")
                    job_status.raise_for_status()

            except requests.exceptions.RequestException as e:
                logger.error(red(f"Error {e} checking status of Python job {job_location}  for model {self.identifier}"))
                raise dbt.exceptions.DbtRuntimeError(f"Error checking status for job {job_location}")

            time.sleep(DEFAULT_DELAY_BETWEEN_POLL_IN_SECONDS)
        logger.error(red(f"Timeout error for Python model {self.identifier}"))
        raise dbt.exceptions.DbtRuntimeError(f"Timeout error for Python model {self.identifier}")

    def __call__(self, *args, **kwargs):
        data = {
            "service": self.service
        }
        if self.async_flag:
            data["asyncFlag"] = self.async_flag
            data["timeout"] = self.timeout
        if self.conda_env_name:
            data["envName"] = self.conda_env_name

        if self.async_flag:
            self.schedule_async_job_and_wait_for_completion(data=data)
        else:  # Run in blocking mode
            logger.info(f"Running Python model {self.identifier} with args {data}")
            try:
                r = self.oml4py_client.request(method="POST",
                                               path=OML_DO_EVAL_API.format(script_name=self.py_q_script_name),
                                               data=json.dumps(data),
                                               raise_for_status=False)
                job_result = r.json()
                if 'errorMessage' in job_result:
                    logger.error(red(f"FAILURE - Python model {self.identifier} Job failure is: {job_result}"))
                    raise dbt.exceptions.DbtRuntimeError(f"Error running Python model {self.identifier}")
                r.raise_for_status()
                logger.info(green(f"SUCCESS - Python model {self.identifier} Job result is: {job_result}"))
            except requests.exceptions.RequestException as e:
                logger.error(red(f"Error {e} running Python model {self.identifier}"))
                raise dbt.exceptions.DbtRuntimeError(f"Error running Python model {self.identifier}")

