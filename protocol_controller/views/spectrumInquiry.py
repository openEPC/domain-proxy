from flask import Blueprint, request
from flask_json import as_json

from protocol_controller.grpc_communication.get_common_rc_response import get_common_bulk_rc_response

spectrum_inquiry_page = Blueprint("spectrumInquiry", __name__)


@spectrum_inquiry_page.route('/spectrumInquiry', methods=('POST', ))
@as_json
def spectrum_inquiry():
    return get_common_bulk_rc_response(request, "spectrumInquiryResponse")