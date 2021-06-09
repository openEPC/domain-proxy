from flask import Blueprint, request
from flask_json import as_json

from protocol_controller.grpc_communication.get_common_rc_response import get_common_bulk_rc_response

grant_page = Blueprint("grant", __name__)


@grant_page.route('/grant', methods=('POST', ))
@as_json
def grant():
    return get_common_bulk_rc_response(request, "grantResponse")