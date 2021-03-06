from typing import Optional

import flask
from flask import Request

from MikrotikBackup.infrastructure import request_dict, cookie_auth
from MikrotikBackup.services import user_service


class ViewModelBase:
    def __init__(self):
        self.request: Request = flask.request
        self.request_dict = request_dict.create('')

        self.error: Optional[str] = None
        self.user_id: Optional[int] = cookie_auth.get_user_id_via_auth_cookie(self.request)
        self.user = user_service.find_user_by_id(self.user_id)

    def file_request(self):
        return self.request.files['file']

    def to_dict(self):
        return self.__dict__