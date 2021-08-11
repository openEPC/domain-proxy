from radio_controller.services.radio_controller.strategies.get_cbsd_id import registration_get_cbsd_id, simple_get_cbsd_id
from radio_controller.services.radio_controller.strategies.request_postprocessing import \
    postprocess_spectrum_inquiry_request, default_postprocessing_function

request_strategies = {
    "registrationRequest": {
        "request_postprocessing": default_postprocessing_function,
        "get_cbsd_id": registration_get_cbsd_id,
    },
    "spectrumInquiryRequest": {
        "request_postprocessing": postprocess_spectrum_inquiry_request,
        "get_cbsd_id": simple_get_cbsd_id,
    },
    "grantRequest": {
        "request_postprocessing": default_postprocessing_function,
        "get_cbsd_id": simple_get_cbsd_id,
    },
    "heartbeatRequest": {
        "request_postprocessing": default_postprocessing_function,
        "get_cbsd_id": simple_get_cbsd_id,
    },
    "relinquishmentRequest": {
        "request_postprocessing": default_postprocessing_function,
        "get_cbsd_id": simple_get_cbsd_id,
    },
    "deregistrationRequest": {
        "request_postprocessing": default_postprocessing_function,
        "get_cbsd_id": simple_get_cbsd_id,
    },
}
