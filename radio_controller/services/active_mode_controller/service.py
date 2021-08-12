import logging

from sqlalchemy.orm import joinedload

import active_mode_pb2 as active_mode
from active_mode_pb2 import GetStateRequest, State
from active_mode_pb2_grpc import ActiveModeControllerServicer
from db_service.models import DBActiveModeConfig, DBCbsd, DBGrant, DBGrantState, DBChannel
from db_service.session_manager import SessionManager, Session
from mappings.types import CbsdStates, GrantStates

logger = logging.getLogger(__name__)

cbsd_state_mapping = {
    CbsdStates.UNREGISTERED.value: active_mode.Unregistered,
    CbsdStates.REGISTERED.value: active_mode.Registered,
}

grant_state_mapping = {
    GrantStates.GRANTED.value: active_mode.Granted,
    GrantStates.AUTHORIZED.value: active_mode.Authorized,
}


class ActiveModeControllerService(ActiveModeControllerServicer):
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def GetState(self, request: GetStateRequest, context) -> State:
        logger.info("Getting DB state")
        with self.session_manager.session_scope() as session:
            return self._build_state(session)

    def _build_state(self, session: Session) -> active_mode.State:
        db_configs = session.query(DBActiveModeConfig) \
            .join(DBCbsd).options(
            joinedload(DBActiveModeConfig.cbsd).options(
                joinedload(DBCbsd.channels),
                joinedload(DBCbsd.grants).options(joinedload(DBGrant.state)),
            )
        )
        configs = [self._build_config(session, x) for x in db_configs]
        return active_mode.State(active_mode_configs=configs)

    def _build_config(self, session: Session, config: DBActiveModeConfig) -> active_mode.ActiveModeConfig:
        return active_mode.ActiveModeConfig(
            desired_state=cbsd_state_mapping[config.desired_state.name],
            cbsd=self._build_cbsd(session, config.cbsd),
        )

    def _build_cbsd(self, session: Session, cbsd: DBCbsd) -> active_mode.Cbsd:
        db_grants = session.query(DBGrant).join(DBGrantState).filter(
            DBGrant.cbsd_id == cbsd.id,
            DBGrantState.name != GrantStates.IDLE.value,
        )
        grants = [self._build_grant(x) for x in db_grants]
        channels = [self._build_channel(x) for x in cbsd.channels]
        return active_mode.Cbsd(
            id=cbsd.cbsd_id,
            user_id=cbsd.user_id,
            fcc_id=cbsd.fcc_id,
            serial_number=cbsd.cbsd_serial_number,
            state=cbsd_state_mapping[cbsd.state.name],
            eirp_capability=cbsd.eirp_capability,
            grants=grants,
            channels=channels,
        )

    @staticmethod
    def _build_grant(grant: DBGrant) -> active_mode.Grant:
        return active_mode.Grant(
            id=grant.grant_id,
            state=grant_state_mapping[grant.state.name],
            heartbeat_interval_sec=grant.heartbeat_interval,
            last_heartbeat_timestamp=int(grant.last_heartbeat_request_time.timestamp()),
        )

    @staticmethod
    def _build_channel(channel: DBChannel) -> active_mode.Channel:
        return active_mode.Channel(
            frequency_range=active_mode.FrequencyRange(
                low=channel.low_frequency,
                high=channel.high_frequency,
            ),
            max_eirp=channel.max_eirp,
            last_eirp=channel.last_used_max_eirp,
        )
