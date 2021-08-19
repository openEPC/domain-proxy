import json
import logging
from time import sleep

from active_mode_pb2 import ToggleActiveModeParams
from db_service.db_initialize import DBInitializer
from db_service.models import DBCbsdState, Base, DBActiveModeConfig, DBRequestState, DBRequestType, DBCbsd
from db_service.session_manager import SessionManager
from db_service.tests.db_testcase_default import DBTestCaseDefault
from mappings.types import CbsdStates, Switch
from radio_controller.services.active_mode_controller.service import ActiveModeControllerService, cbsd_state_mapping
from radio_controller.services.radio_controller.service import RadioControllerService
from requests_pb2 import RequestPayload


class ActiveModeControllerTestCase(DBTestCaseDefault):
    def setUp(self):
        super().setUp()
        self.amc_service = ActiveModeControllerService(SessionManager(self.engine))
        self.rc_service = RadioControllerService(SessionManager(self.engine))
        Base.metadata.drop_all()  # Cleaning up after previous tests
        Base.metadata.create_all()
        DBInitializer(SessionManager(self.engine)).initialize()

    def tearDown(self):
        self.session.rollback()
        self.session.close()
        # Base.metadata.drop_all()

    def test_cbsd_auto_registered(self):
        unregistered_state = self.session.query(DBCbsdState).filter(
            DBCbsdState.name == CbsdStates.UNREGISTERED.value).scalar()
        registered_state = self.session.query(DBCbsdState).filter(
            DBCbsdState.name == CbsdStates.REGISTERED.value).scalar()

        request_pending_state = self.session.query(DBRequestState).filter(DBRequestState.name == "pending").scalar()
        registration_type = self.session.query(DBRequestType).filter(
            DBRequestType.name == "registrationRequest").scalar()

        registration_request = {
            "registrationRequest": [
                {
                    "fccId": "foo",
                    "cbsdCategory": "B",
                    "callSign": "WSD987",
                    "userId": "John Doe",
                    "airInterface": {
                        "radioTechnology": "E_UTRA"
                    },
                    "cbsdSerialNumber": "4321dcba",
                    "measCapability": [
                        "RECEIVED_POWER_WITHOUT_GRANT"
                    ],
                    "installationParam": {
                        "latitude": 37.425056,
                        "longitude": -122.084113,
                        "height": 9.3,
                        "heightType": "AGL",
                        "indoorDeployment": False,
                        "antennaAzimuth": 271,
                        "antennaDowntilt": 3,
                        "antennaGain": 16,
                        "antennaBeamwidth": 30
                    },
                    "groupingParam": [
                        {
                            "groupId": "example-group-3",
                            "groupType": "INTERFERENCE_COORDINATION"
                        }
                    ]
                }
            ]
        }

        self.rc_service.UploadRequests(RequestPayload(payload=json.dumps(registration_request)), None)

        cbsd = self.session.query(DBCbsd).first()

        self.amc_service.ToggleActiveMode(ToggleActiveModeParams(
            cbsd_id=cbsd.id,
            switch=Switch.ON.value,
            desired_state=cbsd_state_mapping[CbsdStates.REGISTERED.value]),
            None
        )

        sleep(70)

        self.session.commit()

        cbsd = self.session.query(DBCbsd).first()

        self.assertEqual(CbsdStates.REGISTERED.value, cbsd.state.name)
        self.assertEqual(1, len(cbsd.channels))
        self.assertEqual(1, len(cbsd.grants))
        self.assertEqual(registered_state.id, len(cbsd.active_mode_config.desired_state_id))
