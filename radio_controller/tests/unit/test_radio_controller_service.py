import json

import testing.postgresql
from parameterized import parameterized

from db_service.db_initialize import DBInitializer
from db_service.models import DBRequest, DBResponse, DBCbsd
from db_service.session_manager import SessionManager
from db_service.tests.db_testcase import DBTestCase
from radio_controller.services.radio_controller.service import RadioControllerService

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)


class RadioControllerTestCase(DBTestCase):

    def setUp(self):
        super().setUp()
        self.rc_service = RadioControllerService(SessionManager(self.engine))
        DBInitializer(SessionManager(self.engine)).initialize()

    @parameterized.expand([
        (1, {"foo": "bar"}, {"foo": "bar"}),
        (2, {"foo": "bar"}, {}),
    ])
    def test_get_request_response(self, req_id, db_response_payload, grpc_expected_response_payload):
        # Given
        cbsd = DBCbsd(id=1, cbsd_id="foo1")
        db_request = DBRequest(id=1, cbsd_id=cbsd.id)
        db_response = DBResponse(id=1, request_id=1, response_code=0, payload=db_response_payload)

        self.session.add_all([cbsd, db_request, db_response])
        self.session.commit()

        # When
        grpc_response_payload = json.loads(self.rc_service._get_request_response(req_id).payload)

        # Then
        self.assertEqual(grpc_expected_response_payload, grpc_response_payload)

    @parameterized.expand([
        ({"registrationRequest":
              [{"fccId": "foo1", "cbsdSerialNumber": "foo2"},
               {"fccId": "foo1", "cbsdSerialNumber": "foo2"}]}, [1, 2]),
        ({"deregistrationRequest":
              [{"cbsdId": "foo1"},
               {"cbsdId": "foo1"}]}, []),
        ({"relinquishmentRequest":
              [{"cbsdId": "foo1"},
               {"cbsdId": "foo1"}]}, []),
        ({"heartbeatRequest":
              [{"cbsdId": "foo1"},
               {"cbsdId": "foo1"}]}, []),
        ({"grantRequest":
              [{"cbsdId": "foo1"},
               {"cbsdId": "foo1"}]}, []),
        ({"spectrumInquiryRequest":
              [{"cbsdId": "foo1"},
               {"cbsdId": "foo1"}]}, []),
    ])
    def test_store_requests_from_map_stores_requests_in_db_only_for_registration_reqs(self, request_map, expected_list):
        # Given

        # When
        self.rc_service._store_requests_from_map(request_map)
        db_request_ids = self.session.query(DBRequest.id).all()
        db_request_ids = [_id for (_id,) in db_request_ids]

        # Then
        self.assertListEqual(db_request_ids, expected_list)

    def test_get_or_create_cbsd_doesnt_create_already_existing_entities(self):
        # Given
        payload = {"fccId": "foo1", "cbsdSerialNumber": "foo2"}
        # No cbsds in the db
        # When
        self.rc_service._get_or_create_cbsd(
            self.session,
            "registrationRequest",
            payload,
        )
        self.session.commit()

        cbsd1 = self.session.query(DBCbsd).first()

        self.rc_service._get_or_create_cbsd(
            self.session,
            "registrationRequest",
            payload,
        )
        self.session.commit()
        cbsd2 = self.session.query(DBCbsd).first()

        # Then
        self.assertEqual(cbsd1.id, cbsd2.id)
