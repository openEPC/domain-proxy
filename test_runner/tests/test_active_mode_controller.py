import json
from time import sleep

import grpc

from active_mode_pb2 import ToggleActiveModeParams
from active_mode_pb2_grpc import ActiveModeControllerStub
from db_service.db_initialize import DBInitializer
from db_service.models import DBCbsd
from db_service.session_manager import SessionManager
from db_service.tests.db_testcase import DBTestCase
from fixtures.fake_requests.registration_requests import registration_requests
from mappings.types import CbsdStates, Switch
from radio_controller.services.active_mode_controller.service import cbsd_state_mapping
from requests_pb2 import RequestPayload
from requests_pb2_grpc import RadioControllerStub
from test_runner.config import TestConfig

config = TestConfig()


class ActiveModeControllerTestCase(DBTestCase):

    def setUp(self):
        super().setUp()
        self.grpc_channel = grpc.insecure_channel(f"{config.GRPC_SERVICE}:{config.GRPC_PORT}")
        DBInitializer(SessionManager(self.engine)).initialize()
        self.amc_client = ActiveModeControllerStub(self.grpc_channel)
        self.rc_client = RadioControllerStub(self.grpc_channel)

    def test_cbsd_auto_registered(self):
        # Given
        self.rc_client.UploadRequests(RequestPayload(payload=json.dumps(registration_requests[0])), None)

        cbsd = self.session.query(DBCbsd).first()
        self.session.commit()

        # When
        self.amc_client.ToggleActiveMode(ToggleActiveModeParams(
            cbsd_id=cbsd.id,
            switch=Switch.ON.value,
            desired_state=cbsd_state_mapping[CbsdStates.REGISTERED.value]),
            None
        )

        sleep(100)

        self.session.commit()

        cbsd = self.session.query(DBCbsd).first()

        # Then
        self.assertEqual(CbsdStates.REGISTERED.value, cbsd.state.name)
        self.assertEqual(1, len(cbsd.channels))
        self.assertEqual(1, len(cbsd.grants))
