#
# Copyright (c) 2017 Apstra Inc, <community@apstra.com>
#
# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by
# Ansible still belong to the author of the module, and may assign their own
# license to the complete work.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

"""
This module adds shared support for Apstra AOS modules

In order to use this module, include it as part of your module

from ansible.module_utils.aos import *

"""
import os
import json
import requests
from requests.adapters import HTTPAdapter
from ansible.module_utils.parsing.convert_bool import boolean


def requests_header(session):
    return {'AUTHTOKEN': session['token'],
            'Accept': "application/json",
            'Content-Type': "application/json",
            'cache-control': "no-cache"}


def set_requests_verify():
    return boolean(os.environ.get('AOS_VERIFY_CERTIFICATE', 'True'))


def requests_retry(retries=3, session=None):

    session = session or requests.Session()
    adapter = HTTPAdapter(max_retries=retries)

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


def requests_response(response):
    return response.json() if response.ok else response.raise_for_status()


def aos_get(session, endpoint):
    """
    GET request aginst aos RestApi
    :param session: dict
    :param endpoint: string
    :return: dict
    """
    aos_url = "https://{}/api/{}".format(session['server'], endpoint)
    headers = requests_header(session)
    response = requests_retry().get(aos_url,
                                    headers=headers,
                                    verify=set_requests_verify())

    return requests_response(response)


def aos_post(session, endpoint, payload):
    """
    POST request aginst aos RestApi
    :param session: dict
    :param endpoint: string
    :param payload: string
    :return: dict
    """
    aos_url = "https://{}/api/{}".format(session['server'], endpoint)
    headers = requests_header(session)
    response = requests_retry().post(aos_url,
                                     data=json.dumps(payload),
                                     headers=headers,
                                     verify=set_requests_verify())

    return requests_response(response)


def aos_put(session, endpoint, payload):
    """
    PUT request aginst aos RestApi
    :param session: dict
    :param endpoint: string
    :param payload: string
    :return: dict
    """
    aos_url = "https://{}/api/{}".format(session['server'], endpoint)
    headers = requests_header(session)
    response = requests_retry().put(aos_url,
                                    data=json.dumps(payload),
                                    headers=headers,
                                    verify=set_requests_verify())

    return response


def aos_delete(session, endpoint, aos_id):
    """
    DELETE request aginst aos RestApi
    :param session: dict
    :param endpoint: string
    :param aos_id: string
    :return: dict
    """
    aos_url = "https://{}/api/{}/{}".format(session['server'],
                                            endpoint,
                                            aos_id)
    headers = requests_header(session)
    response = requests_retry().delete(aos_url,
                                       headers=headers,
                                       verify=set_requests_verify())

    return requests_response(response)
