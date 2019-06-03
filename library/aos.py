# Copyright (c) 2017 Apstra Inc, <community@apstra.com>

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


def _find_resource(resource_data, key, keyword):
    for item in resource_data['items']:
        if item[keyword] == key:
            return item
    return {}


def find_resource_by_name(resource_data, name):
    return _find_resource(resource_data, name, "display_name")


def find_resource_by_id(resource_data, uuid):
    return _find_resource(resource_data, uuid, "id")


def find_resource_item(session, endpoint,
                       name=None,
                       uuid=None):
    """
    Find an existing resource based on name or id from a given endpoint
    :param session: dict
    :param endpoint: string
    :param resource_name: string
    :param resource_id: string
    :return: Returns collection item (dict)
    """
    resource_data = aos_get(session, endpoint)

    if name:
        return find_resource_by_name(resource_data, name)
    elif uuid:
        return find_resource_by_id(resource_data, uuid)
    else:
        return {}
