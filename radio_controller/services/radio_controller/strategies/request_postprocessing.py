from db_service.models import DBRequest, DBChannel
from db_service.session_manager import Session


def postprocess_spectrum_inquiry_request(db_request: DBRequest, session: Session):
    _delete_existing_channels(db_request, session)


def default_postprocessing_function(*args, **kwargs):
    pass


def _delete_existing_channels(db_request: DBRequest, session: Session):
    session.query(DBChannel).filter(DBChannel.cbsd_id == db_request.cbsd.id).delete()
