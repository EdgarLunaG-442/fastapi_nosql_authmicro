import requests
import os
from requests.exceptions import ConnectTimeout, ConnectionError, ReadTimeout, Timeout
from urllib3.exceptions import ReadTimeoutError
from common import NotAvailable, AnyCode

NOT_AVAILABLE_MSG = os.getenv('NOT_AVAILABLE_MSG')
ADAPTERS_TIMEOUT = os.getenv('ADAPTERS_TIMEOUT')


def extract_response_data(response):
    try:
        response_data = response.json()
    except Exception as e:
        response_data = response.text
    return response_data


def raise_non_exception_errors(url, code, response_data):
    if int(str(code)[0]) / 2 != 1 and int(str(code)[0]) % 5 != 0:
        if type(response_data) != str:
            raise AnyCode(response_data, code, True)
        else:
            raise AnyCode(response_data, code)
    elif int(str(code)[0]) % 5 == 0:
        raise NotAvailable(NOT_AVAILABLE_MSG)


def get(url: str, params: any = None, data: any = None, headers: any = None):
    try:
        response = requests.get(url, params=params, data=data, headers=headers, timeout=int(ADAPTERS_TIMEOUT))
        code = response.status_code
        response_data = extract_response_data(response)
        raise_non_exception_errors(url, code, response_data)
        return code, response_data
    except (ConnectTimeout, ConnectionError, ReadTimeoutError, ReadTimeout, Timeout) as e:
        raise NotAvailable(NOT_AVAILABLE_MSG)


def post(url: str, params: any = None, data: any = None, headers: any = None):
    try:
        response = requests.post(url, params=params, data=data, headers=headers, timeout=int(ADAPTERS_TIMEOUT))
        code = response.status_code
        response_data = extract_response_data(response)
        raise_non_exception_errors(url, code, response_data)
        return code, response_data
    except (ConnectTimeout, ConnectionError, ReadTimeoutError, ReadTimeout, Timeout) as e:
        raise NotAvailable(NOT_AVAILABLE_MSG)
