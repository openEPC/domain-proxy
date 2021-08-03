from db_service.session_manager import SessionManager
from active_mode_pb2 import GetStateRequest, State
from active_mode_pb2_grpc import ActiveModeControllerServicer

class ActiveModeControllerService(ActiveModeControllerServicer):
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def GetState(self, request: GetStateRequest, context) -> State:
        logger.info("Getting DB state")
        return State()